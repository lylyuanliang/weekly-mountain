package com.weeklymountain.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.BridgeWebViewClient;

public class MainActivity extends BridgeActivity {
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
