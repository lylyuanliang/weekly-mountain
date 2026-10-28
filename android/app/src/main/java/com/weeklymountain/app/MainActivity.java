package com.weeklymountain.app;

import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import android.provider.Settings;
import com.getcapacitor.BridgeActivity;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.atomic.AtomicBoolean;

public class MainActivity extends BridgeActivity {

    // 全局待安装 APK 引用（在授予权限返回或重复调用时免去重新下载）
    private static volatile File pendingInstallApk = null;
    // 标记是否处于引导开启未知应用安装权限的等待流中
    private static volatile boolean waitingForInstallPermission = false;
    // 标记当前是否有下载任务正在进行
    private static final AtomicBoolean isDownloading = new AtomicBoolean(false);
    // 最新进度快照，供切屏重新激活应用 (onResume) 时补发给前端 WebView
    private static volatile int lastPercent = 0;
    private static volatile long lastReceived = 0;
    private static volatile long lastTotal = 0;
    private static volatile String lastStatus = "idle";
    private static volatile String lastMessage = "";

    public class AlpineNativeBridge {
        private final Context context;

        public AlpineNativeBridge(Context context) {
            this.context = context;
        }

        @JavascriptInterface
        public boolean isNativeApp() {
            return true;
        }

        @JavascriptInterface
        public boolean saveImageToGallery(String base64Data, String filename) {
            try {
                if (base64Data == null || base64Data.trim().isEmpty()) {
                    return false;
                }
                String cleanBase64 = base64Data;
                if (cleanBase64.contains(",")) {
                    cleanBase64 = cleanBase64.substring(cleanBase64.indexOf(",") + 1);
                }
                byte[] decodedBytes = Base64.decode(cleanBase64, Base64.DEFAULT);
                Bitmap bitmap = BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
                if (bitmap == null) {
                    return false;
                }

                String name = (filename != null && !filename.trim().isEmpty())
                        ? filename.trim()
                        : ("Alpine-Explorer-" + System.currentTimeMillis() + ".png");
                if (!name.toLowerCase().endsWith(".png")) {
                    name += ".png";
                }

                boolean success = false;
                Uri savedUri = null;

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    ContentValues values = new ContentValues();
                    values.put(MediaStore.Images.Media.DISPLAY_NAME, name);
                    values.put(MediaStore.Images.Media.MIME_TYPE, "image/png");
                    values.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/AlpineExplorer");
                    values.put(MediaStore.Images.Media.IS_PENDING, 1);

                    Uri collection = MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
                    savedUri = context.getContentResolver().insert(collection, values);

                    if (savedUri != null) {
                        try (OutputStream out = context.getContentResolver().openOutputStream(savedUri)) {
                            if (out != null) {
                                bitmap.compress(Bitmap.CompressFormat.PNG, 100, out);
                                success = true;
                            }
                        }
                        values.clear();
                        values.put(MediaStore.Images.Media.IS_PENDING, 0);
                        context.getContentResolver().update(savedUri, values, null, null);
                    }
                } else {
                    File picturesDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES);
                    File appDir = new File(picturesDir, "AlpineExplorer");
                    if (!appDir.exists()) {
                        appDir.mkdirs();
                    }
                    File imageFile = new File(appDir, name);
                    try (FileOutputStream fos = new FileOutputStream(imageFile)) {
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100, fos);
                        success = true;
                    }
                    Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
                    savedUri = Uri.fromFile(imageFile);
                    mediaScanIntent.setData(savedUri);
                    context.sendBroadcast(mediaScanIntent);
                }

                if (success) {
                    runOnUiThread(() -> Toast.makeText(context, "🎉 海报已成功保存至手机系统相册！", Toast.LENGTH_LONG).show());
                    return true;
                }
            } catch (Exception e) {
                e.printStackTrace();
                runOnUiThread(() -> Toast.makeText(context, "保存相册失败: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }
            return false;
        }

                /**
         * 检测当前是否具备安装未知来源应用权限 (Android 8.0+)
         */
         @JavascriptInterface
        public boolean canRequestPackageInstalls() {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                return context.getPackageManager().canRequestPackageInstalls();
            }
            return true;
        }

        /**
         * 引导跳转至系统未知来源安装权限设置页面
         */
        @JavascriptInterface
        public void openInstallPermissionSettings() {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                try {
                    waitingForInstallPermission = true;
                    Intent intent = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES);
                    intent.setData(Uri.parse("package:" + context.getPackageName()));
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    context.startActivity(intent);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }

        /**
         * 检查指定版本的安装包是否已经在本地完整就绪
         */
        @JavascriptInterface
        public boolean hasDownloadedApk(String targetVersion) {
            String verStr = (targetVersion != null && !targetVersion.trim().isEmpty())
                    ? targetVersion.trim().replace("v", "")
                    : "latest";
            File updatesDir = new File(context.getCacheDir(), "updates");
            File targetFile = new File(updatesDir, "weekly-mountain-v" + verStr + ".apk");
            return targetFile.exists() && targetFile.length() > 1024 * 1024;
        }

        /**
         * 直接调起已下载安装包的安装
         */
        @JavascriptInterface
        public void installDownloadedApk() {
            if (pendingInstallApk != null && pendingInstallApk.exists() && pendingInstallApk.length() > 0) {
                runOnUiThread(() -> triggerApkInstall(pendingInstallApk));
            }
        }

        /**
         * 主动清理下载目录下的所有临时安装包 APK 文件
         */
        @JavascriptInterface
        public boolean cleanApkCache() {
            cleanUpdateApkCache(context, true);
            return true;
        }

        /**
         * 取消当前进行中的 APK 下载任务
         */
        @JavascriptInterface
        public void cancelDownload() {
            isDownloading.set(false);
            lastStatus = "cancelled";
            notifyJsUpdateStatus("cancelled", 0, 0, 0, "用户已取消下载");
        }

        /**
         * 在应用内流式下载最新 APK 并直接唤起安装
         * 核心特性：
         * 1. 命中已完整下载包直接调起安装，0 毫秒重入，杜绝重复浪费流量；
         * 2. 下载期间使用 .apk.download 临时隔离，避免切屏误删；
         * 3. 申请 Partial WakeLock 保证切到微信或设置时下载不中断；
         * 4. 切屏返回时实时同步最新进度。
         */
        @JavascriptInterface
        public void downloadAndInstallApk(final String downloadUrl, final String targetVersion) {
            if (downloadUrl == null || downloadUrl.trim().isEmpty()) {
                notifyJsUpdateStatus("error", 0, 0, 0, "下载地址为空");
                return;
            }

            File updatesDir = new File(context.getCacheDir(), "updates");
            if (!updatesDir.exists()) {
                updatesDir.mkdirs();
            }

            String verStr = (targetVersion != null && !targetVersion.trim().isEmpty())
                    ? targetVersion.trim().replace("v", "")
                    : "latest";
            File targetFile = new File(updatesDir, "weekly-mountain-v" + verStr + ".apk");

            // 关键优化 1：若已存在完整且大小合规的安装包（>1MB），直接进入安装流程，杜绝重复下载！
            if (targetFile.exists() && targetFile.length() > 1024 * 1024 && !isDownloading.get()) {
                pendingInstallApk = targetFile;
                lastStatus = "installing";
                lastPercent = 100;
                lastReceived = targetFile.length();
                lastTotal = targetFile.length();
                lastMessage = "已检测到完整安装包，正在调起安装...";
                notifyJsUpdateStatus("installing", 100, targetFile.length(), targetFile.length(), "已检测到完整安装包，正在调起安装...");
                runOnUiThread(() -> triggerApkInstall(targetFile));
                return;
            }

            // 关键优化 2：若当前任务正在下载中，不重复开启线程，而是立即回传最新进度
            if (isDownloading.get()) {
                notifyJsUpdateStatus(lastStatus, lastPercent, lastReceived, lastTotal, lastMessage);
                return;
            }

            // 清理除当前下载外的历史无效临时文件
            cleanUpdateApkCache(context, false);

            isDownloading.set(true);
            lastStatus = "downloading";
            lastPercent = 0;
            lastReceived = 0;
            lastTotal = 0;
            lastMessage = "正在连接高速节点...";
            notifyJsUpdateStatus("downloading", 0, 0, 0, "正在连接高速节点...");

            new Thread(() -> {
                InputStream input = null;
                OutputStream output = null;
                HttpURLConnection connection = null;
                PowerManager.WakeLock wakeLock = null;
                File tempFile = new File(updatesDir, "weekly-mountain-v" + verStr + ".apk.download");

                try {
                    // 获取 Partial WakeLock 保证切到后台时 CPU 持续运行网络下载
                    PowerManager pm = (PowerManager) context.getSystemService(Context.POWER_SERVICE);
                    if (pm != null) {
                        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "WeeklyMountain:DownloadWakeLock");
                        wakeLock.acquire(10 * 60 * 1000L); // 最长锁 10 分钟
                    }

                    if (tempFile.exists()) {
                        tempFile.delete();
                    }

                    URL url = new URL(downloadUrl);
                    connection = (HttpURLConnection) url.openConnection();
                    connection.setInstanceFollowRedirects(true);
                    connection.setConnectTimeout(15000);
                    connection.setReadTimeout(30000);
                    connection.setRequestProperty("User-Agent", "Mozilla/5.0 WeeklyMountain-AppUpdate");
                    connection.connect();

                    int responseCode = connection.getResponseCode();
                    // 处理 301/302 重定向
                    if (responseCode == HttpURLConnection.HTTP_MOVED_PERM || responseCode == HttpURLConnection.HTTP_MOVED_TEMP || responseCode == 307 || responseCode == 308) {
                        String newUrl = connection.getHeaderField("Location");
                        if (newUrl != null) {
                            connection.disconnect();
                            url = new URL(newUrl);
                            connection = (HttpURLConnection) url.openConnection();
                            connection.setInstanceFollowRedirects(true);
                            connection.setConnectTimeout(15000);
                            connection.setReadTimeout(30000);
                            connection.setRequestProperty("User-Agent", "Mozilla/5.0 WeeklyMountain-AppUpdate");
                            connection.connect();
                            responseCode = connection.getResponseCode();
                        }
                    }

                    if (responseCode != HttpURLConnection.HTTP_OK) {
                        throw new Exception("下载服务器响应失败 (HTTP " + responseCode + ")");
                    }

                    int fileLength = connection.getContentLength();
                    input = connection.getInputStream();
                    output = new FileOutputStream(tempFile);

                    byte[] data = new byte[8192];
                    long total = 0;
                    int count;
                    long lastUpdateTime = System.currentTimeMillis();
                    long lastBytes = 0;
                    double speedKb = 0;

                    while ((count = input.read(data)) != -1) {
                        if (!isDownloading.get()) {
                            if (tempFile.exists()) tempFile.delete();
                            return;
                        }

                        total += count;
                        output.write(data, 0, count);

                        long now = System.currentTimeMillis();
                        if (now - lastUpdateTime >= 250) {
                            long durationMs = now - lastUpdateTime;
                            if (durationMs > 0) {
                                speedKb = (double) (total - lastBytes) / (durationMs / 1000.0) / 1024.0;
                            }
                            lastUpdateTime = now;
                            lastBytes = total;

                            int percent = fileLength > 0 ? (int) (total * 100 / fileLength) : 0;
                            String speedText = String.format("%.1f KB/s", speedKb);
                            if (speedKb >= 1024) {
                                speedText = String.format("%.2f MB/s", speedKb / 1024.0);
                            }
                            lastPercent = percent;
                            lastReceived = total;
                            lastTotal = fileLength;
                            lastStatus = "downloading";
                            lastMessage = speedText;
                            notifyJsUpdateStatus("downloading", percent, total, fileLength, speedText);
                        }
                    }

                    output.flush();

                    // 下载完成：将 .download 临时文件原子重命名为正式 .apk
                    if (targetFile.exists()) {
                        targetFile.delete();
                    }
                    boolean renamed = tempFile.renameTo(targetFile);
                    File finalApk = renamed ? targetFile : tempFile;

                    pendingInstallApk = finalApk;
                    lastStatus = "installing";
                    lastPercent = 100;
                    lastReceived = total;
                    lastTotal = total;
                    lastMessage = "下载完成，正在唤起安装...";
                    notifyJsUpdateStatus("installing", 100, total, total, "下载完成，正在唤起安装...");

                    // 唤起系统安装界面
                    runOnUiThread(() -> triggerApkInstall(finalApk));

                } catch (Exception e) {
                    e.printStackTrace();
                    if (tempFile.exists()) {
                        tempFile.delete();
                    }
                    lastStatus = "error";
                    lastMessage = "下载失败: " + e.getMessage();
                    notifyJsUpdateStatus("error", 0, 0, 0, "下载失败: " + e.getMessage());
                } finally {
                    isDownloading.set(false);
                    if (wakeLock != null && wakeLock.isHeld()) {
                        try {
                            wakeLock.release();
                        } catch (Exception ignored) {
                        }
                    }
                    try {
                        if (output != null) output.close();
                        if (input != null) input.close();
                        if (connection != null) connection.disconnect();
                    } catch (Exception ignored) {
                    }
                }
            }).start();
        }

    }

    /**
     * 唤起系统 PackageInstaller 安装已下载的 APK
     */
    public void triggerApkInstall(File apkFile) {
        try {
            if (apkFile == null || !apkFile.exists() || apkFile.length() <= 0) {
                Toast.makeText(this, "安装包不存在或已损坏", Toast.LENGTH_SHORT).show();
                notifyJsUpdateStatus("error", 0, 0, 0, "安装包不存在或损坏");
                return;
            }

            pendingInstallApk = apkFile;

            // Android 8.0+ 权限二次拦截保障
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                if (!getPackageManager().canRequestPackageInstalls()) {
                    waitingForInstallPermission = true;
                    Toast.makeText(this, "请在设置中开启「允许安装未知应用」权限，返回将自动继续安装", Toast.LENGTH_LONG).show();
                    Intent intent = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES);
                    intent.setData(Uri.parse("package:" + getPackageName()));
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(intent);
                    lastStatus = "permission_required";
                    lastMessage = "等待授予安装权限";
                    notifyJsUpdateStatus("permission_required", 100, apkFile.length(), apkFile.length(), "等待授予安装权限");
                    return;
                }
            }

            waitingForInstallPermission = false;
            Uri apkUri = FileProvider.getUriForFile(this, getPackageName() + ".fileprovider", apkFile);
            Intent installIntent = new Intent(Intent.ACTION_VIEW);
            installIntent.setDataAndType(apkUri, "application/vnd.android.package-archive");
            installIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            installIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

            startActivity(installIntent);
            lastStatus = "completed";
            lastMessage = "已成功唤起系统安装";
            notifyJsUpdateStatus("completed", 100, apkFile.length(), apkFile.length(), "已成功唤起系统安装");
        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(this, "调起安装失败: " + e.getMessage(), Toast.LENGTH_LONG).show();
            lastStatus = "error";
            lastMessage = "调起安装失败: " + e.getMessage();
            notifyJsUpdateStatus("error", 0, 0, 0, "调起安装失败: " + e.getMessage());
        }
    }

    /**
     * 统一向 WebView 前端注入进度与状态事件
     */
    public void notifyJsUpdateStatus(String status, int percent, long received, long total, String msg) {
        runOnUiThread(() -> {
            if (bridge != null && bridge.getWebView() != null) {
                String cleanMsg = (msg != null) ? msg.replace("\"", "\\\"").replace("\n", " ").replace("\r", " ") : "";
                String js = String.format(
                        "if (window.onAlpineDownloadProgress) { window.onAlpineDownloadProgress({ status: '%s', percent: %d, receivedBytes: %d, totalBytes: %d, message: '%s' }); }",
                        status, percent, received, total, cleanMsg
                );
                bridge.getWebView().evaluateJavascript(js, null);
            }
        });
    }

    /**
     * 安全清理缓存目录下的旧更新安装包 (APK)，释放手机存储空间
     * 规则：
     * 1. 绝不删除当前 pendingInstallApk；
     * 2. 下载中时绝不删除 .download 临时文件；
     * 3. 仅在冷启动或显式清理时执行。
     */
    public static void cleanUpdateApkCache(Context context) {
        cleanUpdateApkCache(context, false);
    }

    public static void cleanUpdateApkCache(Context context, boolean forceAll) {
        if (context == null) return;
        new Thread(() -> {
            try {
                File updatesDir = new File(context.getCacheDir(), "updates");
                if (updatesDir.exists() && updatesDir.isDirectory()) {
                    File[] files = updatesDir.listFiles();
                    if (files != null) {
                        for (File f : files) {
                            if (!f.isFile()) continue;
                            String name = f.getName().toLowerCase();
                            if (!forceAll) {
                                if (pendingInstallApk != null && f.getAbsolutePath().equals(pendingInstallApk.getAbsolutePath())) {
                                    continue;
                                }
                                if (isDownloading.get() && name.endsWith(".download")) {
                                    continue;
                                }
                            }
                            if (name.endsWith(".apk") || name.endsWith(".download") || name.endsWith(".tmp")) {
                                f.delete();
                            }
                        }
                    }
                }
            } catch (Exception ignored) {
            }
        }).start();
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 应用冷启动时自动扫描并清理已完成安装的历史残留 APK
        cleanUpdateApkCache(this, false);

        // 仅在 DEBUGgable 编译模式下开启 WebView 远程调试，RELEASE 模式严格关闭防止 USB 审查
        if ((getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
            WebView.setWebContentsDebuggingEnabled(true);
        }
        if (bridge != null && bridge.getWebView() != null) {
            WebView webView = bridge.getWebView();
            WebSettings settings = webView.getSettings();
            if (settings != null) {
                settings.setCacheMode(WebSettings.LOAD_DEFAULT);
                settings.setDomStorageEnabled(true);
            }
            webView.addJavascriptInterface(new AlpineNativeBridge(this), "AlpineNative");
        }
    }

    @Override
    public void onResume() {
        super.onResume();

        // 1. 核心闭环：若此前正在等待开启安装权限，且用户在系统设置开启后返回，自动继续拉起安装！
        if (waitingForInstallPermission && pendingInstallApk != null && pendingInstallApk.exists()) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                if (getPackageManager().canRequestPackageInstalls()) {
                    waitingForInstallPermission = false;
                    File toInstall = pendingInstallApk;
                    runOnUiThread(() -> triggerApkInstall(toInstall));
                    return;
                }
            }
        }

        // 2. 切屏返回时向 WebView 补发当前最新下载进度，防止切屏导致前端进度条卡住
        if (isDownloading.get() && bridge != null && bridge.getWebView() != null) {
            notifyJsUpdateStatus(lastStatus, lastPercent, lastReceived, lastTotal, lastMessage);
        }

        // 3. 注意：严禁在 onResume 盲目调用 cleanUpdateApkCache，避免切屏时误删下载中的文件或待安装文件！

        if (bridge != null && bridge.getWebView() != null) {
            WebView webView = bridge.getWebView();
            webView.postInvalidate();
        }
    }
}
