package com.weeklymountain.app;

import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.Toast;
import com.getcapacitor.BridgeActivity;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

public class MainActivity extends BridgeActivity {

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
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // 显式开启 WebView 远程调试支持
        WebView.setWebContentsDebuggingEnabled(true);
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
        if (bridge != null && bridge.getWebView() != null) {
            WebView webView = bridge.getWebView();
            webView.postInvalidate();
        }
    }
}
