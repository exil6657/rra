# Rust Raid Alarm

Rust Raid Alarm is a local cross-device alert dashboard. It watches an **opt-in rectangle of your own laptop screen** for a configured phrase and/or reference image. When a match persists for the configured number of frames, it triggers the laptop alarm and can synchronize active/cooldown state through Firebase to the Android companion.

## Privacy and boundaries

This project does not use Discord tokens, Discord bots, Discord APIs, self-bots, webhooks, message scraping, or third-party UI automation. The desktop monitor captures only the rectangle you explicitly draw. Images and OCR text remain in memory locally; they are never sent to a network service. Firebase is used only for alarm state when you configure it.

## Requirements

- Windows 10/11 laptop, Python 3.11+, and Tesseract OCR installed
- Android 8.0+ and Android Studio (for the Android companion)
- Optional Firebase Realtime Database project for laptop/phone synchronization

## Laptop setup

```powershell
cd laptop_app
py -3.11 -m pip install -r requirements.txt
py -3.11 main.py
```

On first run, accept the local-monitor disclosure. Open **Settings → Screen Monitor** and:

1. Click **Select screen rectangle** and drag over the exact notification/banner area you want to inspect.
2. Enter a trigger phrase, such as the visible name/mention text expected in that area.
3. Optionally display the desired banner and choose **Capture current region as reference image**. This adds OpenCV local image matching.
4. Set a 100–5000 ms interval and the number of consecutive matching frames needed to alert, then save.
5. Restart the app or complete setup with this configured region. The dashboard is green only while monitoring is active.

Phrase matching requires [Tesseract OCR](https://github.com/tesseract-ocr/tesseract). Install it and ensure `tesseract` is on your system `PATH`. Image-only matching works without Tesseract if no phrase is configured.

## Alert behavior

- A text phrase **or** reference image match that persists for the configured frames sets off the alarm.
- The detector latches while the same cue remains visible, avoiding repeated alerts from one banner.
- Cooldown blocks newly detected cues; **Acknowledge** stops sound/flash and begins cooldown; **Raid Over** clears it early.
- Quiet hours force stealth mode, and auto-silence stops an unacknowledged alarm.
- No Discord data, credential, or interaction is involved.

## Firebase setup (optional)

1. Create a Firebase Realtime Database at [Firebase Console](https://console.firebase.google.com).
2. In **Authentication → Sign-in method**, enable **Anonymous** authentication. The Android client signs in anonymously before accessing the authenticated database rules.
3. Create a service-account key for the laptop and enter its JSON plus database URL in **Settings → Integrations**.
4. Register Android package `com.rustraid`, download `google-services.json`, and put it in `android_app/app/` (it is ignored by Git).
5. Adapt and publish `firebase/database_rules.json` with Firebase Authentication enabled. Do not use test-mode rules in production.

## Android build

1. Open `android_app` in Android Studio.
2. Add `android_app/app/google-services.json` for the same Firebase project.
3. Sync Gradle and select **Build → Build APK(s)**.
4. Install the APK and grant notifications/vibration permissions. The foreground service watches the Firebase alarm state.

## Troubleshooting

- **No detection:** ensure the selected region covers the visible cue, raise its size slightly, verify Tesseract installation for text matching, and try a less-specific phrase.
- **False alerts:** increase consecutive-frame confirmation, tighten the crop, or use a captured visual reference.
- **Reference never matches:** recapture at the same display scaling, theme, and application zoom; image matching is sensitive to visual changes.
- **Phone does not alert:** check Firebase credentials/rules, network connectivity, Android notifications, and foreground-service status.
- **No laptop audio:** verify the bundled original WAV tones are present, or choose a custom audio file in Alarm Settings.
