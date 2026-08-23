package com.influent.launcher;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/**
 * Influent's Android-side launcher. The Linux host communicates with this
 * component through explicit intents after the C++ bridge has selected a
 * package. No shell command or arbitrary URI is accepted here.
 */
public final class MainActivity extends Activity {
    private final List<ResolveInfo> launchableApps = new ArrayList<>();
    private PackageManager packageManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        packageManager = getPackageManager();
        buildUserInterface();
        handleIntent(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIntent(intent);
    }

    private void buildUserInterface() {
        final int orange = Color.rgb(233, 84, 32);
        final int purple = Color.rgb(119, 41, 83);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.WHITE);

        TextView header = new TextView(this);
        header.setText("Influent Apps");
        header.setTextColor(Color.WHITE);
        header.setTextSize(22.0f);
        header.setGravity(Gravity.CENTER_VERTICAL);
        header.setPadding(28, 0, 20, 0);
        header.setBackgroundColor(purple);
        root.addView(header, new LinearLayout.LayoutParams(-1, 72));

        TextView subtitle = new TextView(this);
        subtitle.setText("Aplicaciones Android disponibles");
        subtitle.setTextColor(Color.DKGRAY);
        subtitle.setTextSize(15.0f);
        subtitle.setPadding(28, 22, 20, 14);
        root.addView(subtitle, new LinearLayout.LayoutParams(-1, -2));

        final ListView appList = new ListView(this);
        appList.setDividerHeight(1);
        loadLaunchableApps();
        appList.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, appNames()));
        appList.setOnItemClickListener((parent, view, position, id) -> launchPackage(launchableApps.get(position).activityInfo.packageName));
        root.addView(appList, new LinearLayout.LayoutParams(-1, 0, 1.0f));

        TextView footer = new TextView(this);
        footer.setText("Capa Android de Influent OS");
        footer.setTextColor(orange);
        footer.setGravity(Gravity.CENTER);
        footer.setPadding(12, 12, 12, 18);
        root.addView(footer, new LinearLayout.LayoutParams(-1, -2));

        setContentView(root);
    }

    private void loadLaunchableApps() {
        Intent query = new Intent(Intent.ACTION_MAIN);
        query.addCategory(Intent.CATEGORY_LAUNCHER);
        launchableApps.clear();
        launchableApps.addAll(packageManager.queryIntentActivities(query, PackageManager.MATCH_ALL));
        Collections.sort(launchableApps, Comparator.comparing(info -> info.loadLabel(packageManager).toString(), String.CASE_INSENSITIVE_ORDER));
    }

    private List<String> appNames() {
        List<String> names = new ArrayList<>();
        for (ResolveInfo info : launchableApps) {
            names.add(info.loadLabel(packageManager).toString());
        }
        return names;
    }

    private void handleIntent(Intent intent) {
        if (intent == null || !"com.influent.launcher.OPEN_PACKAGE".equals(intent.getAction())) {
            return;
        }
        String packageName = intent.getStringExtra("package");
        if (packageName != null && packageName.matches("[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)*")) {
            launchPackage(packageName);
        } else {
            Toast.makeText(this, "Identificador de aplicación no válido", Toast.LENGTH_SHORT).show();
        }
    }

    private void launchPackage(String packageName) {
        Intent launchIntent = packageManager.getLaunchIntentForPackage(packageName);
        if (launchIntent == null) {
            Toast.makeText(this, "La aplicación no tiene una actividad lanzable", Toast.LENGTH_SHORT).show();
            return;
        }
        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            startActivity(launchIntent);
        } catch (ActivityNotFoundException exception) {
            Toast.makeText(this, "No se pudo iniciar la aplicación", Toast.LENGTH_SHORT).show();
        }
    }
}
