# Rust Raid Alarm

Rust Raid Alarm is a private laptop-and-phone alert system. The Windows app watches an **opt-in visible screen rectangle** for an OCR phrase and/or image reference. On a match it runs a laptop alarm and, when configured, wakes a **single explicitly paired Android phone** through Firebase Cloud Messaging (FCM).

This project does **not** use Discord accounts, Discord user tokens, Discord bots, self-bots, message scraping, or third-party app automation. The selected screen pixels are processed locally and are never uploaded.

> **Current release status:** source and setup tooling are under active development. Follow this guide only after using the matching release/commit. A real Windows EXE and Android APK still need to be built and validated in their respective local build environments.

## 1. What you need

### Laptop

- Windows 10/11
- Python 3.11+
- Tesseract OCR installed and available on `PATH` for phrase matching
- Internet access for Firebase/phone alerts

### Phone

- Android 8.0+ (API 26+)
- Internet access
- Android Studio and JDK 17 only if you are building the APK yourself

### Accounts and files

- A Google/Firebase account and Firebase project
- `google-services.json` for the Android app
- A Firebase service-account JSON key for the laptop only

Never send, commit, or share the service-account JSON.

## 2. Firebase project setup

### Create the project and database

1. Go to [Firebase Console](https://console.firebase.google.com) and create a project.
2. Open **Build → Realtime Database** and create a database.
3. Copy its URL, for example:

   ```text
   https://your-project-default-rtdb.europe-west1.firebasedatabase.app/
   ```

4. Open **Build → Authentication → Sign-in method**.
5. Enable **Anonymous** authentication.

### Register the Android app

1. Open **Project settings → Your apps → Add app → Android**.
2. Enter this exact package name:

   ```text
   com.rustraid
   ```

3. Download `google-services.json`.
4. Copy it to this exact path:

   ```text
   android_app/app/google-services.json
   ```

Do not rename the file. It is intentionally ignored by Git.

### Create the laptop service account

1. Open **Project settings → Service accounts**.
2. Select **Python** in the Admin SDK guidance.
3. Click **Generate new private key**.
4. Store the downloaded JSON in a private location on the laptop, such as:

   ```text
   Documents\RustRaidAlarm\firebase-service-account.json
   ```

The service-account key is used only by the laptop to manage its paired device and send FCM wake alerts. Do not put it in the Android app.

### Publish database rules

When the pairing implementation is included in your release, open:

```text
Build → Realtime Database → Rules
```

Replace the rules with the contents of:

```text
firebase/database_rules.json
```

Then click **Publish**.

These rules deny access by default, permit authenticated pairing/unlink requests, and grant a paired phone access only to its specific laptop namespace. Do not use Firebase test-mode/open rules.

## 3. Build or run the laptop app

### Run from source

Open Command Prompt or PowerShell:

```powershell
cd path\to\rra\laptop_app
py -3.11 -m pip install -r requirements.txt
py -3.11 main.py
```

### Build the Windows EXE

On Windows, from the same folder:

```bat
build.bat
```

The expected output is:

```text
laptop_app\dist\RustRaidAlarm\RustRaidAlarm.exe
```

Run the EXE from that folder so its bundled assets are available.

## 4. First-run laptop setup

1. Accept the local screen-monitor disclosure.
2. Draw a rectangle around the visible notification/banner area that should trigger the alarm.
3. Enter the text expected in that region, such as your visible display name.
4. Complete setup and open the dashboard.
5. Open **Settings → Screen Monitor**.
6. Use **Check OCR engine**. If unavailable, install Tesseract and restart the app.
7. Use **Test selected region now** to inspect local OCR output and image-match confidence.
8. Optionally capture or select a reference image.
9. Open **Settings → Alarm** and choose volume, preset, TTS, flash, and device target.

The bundled DEFCON sound is an original pulsed wake pattern. Test at a safe volume before relying on it overnight.

## 5. Connect the laptop to Firebase

On the laptop:

1. Open **Settings → Integrations**.
2. Enter the Firebase Realtime Database URL.
3. Open the service-account JSON file locally and paste its full contents into the service-account field.
4. Click **Save and test Firebase**.
5. Confirm the dashboard reports:

   ```text
   Firebase: connected ✓
   ```

The service-account JSON remains in local app configuration only. It must not be committed to Git.

## 6. Build and install the Android APK

1. Install Android Studio and use JDK 17.
2. Open the `android_app` folder in Android Studio.
3. Confirm this file exists:

   ```text
   android_app/app/google-services.json
   ```

4. Allow Gradle sync to complete.
5. Select:

   ```text
   Build → Build Bundle(s) / APK(s) → Build APK(s)
   ```

6. Install the generated debug APK, normally found at:

   ```text
   android_app/app/build/outputs/apk/debug/app-debug.apk
   ```

7. Open the app on the phone and allow notifications.
8. In Android Settings inside Rust Raid Alarm, allow:

   - battery-optimization exemption;
   - full-screen wake alarms;
   - notification permission.

## 7. Pair the phone to the laptop

The system supports **one phone per laptop**. Pairing a replacement phone requires unlinking the current phone first.

### On the laptop

1. Open:

   ```text
   Settings → Pair Phone
   ```

2. Leave the laptop app running.
3. The screen displays a QR code and a full manual pairing code.

### On the phone

1. Open Rust Raid Alarm.
2. Tap **Scan laptop QR code** and scan the QR from the laptop screen.
3. If scanning is unavailable, paste/type the full manual code shown by the laptop.
4. Enter a friendly phone name.
5. Tap **Request link**.
6. Keep both apps open while the laptop verifies the request.

After acceptance:

```text
Phone becomes linked
→ phone starts scoped Firebase monitoring
→ laptop stores that phone’s FCM token
→ alerts route only to that phone
```

The laptop Pair Phone page reports the linked phone name. The Android app exposes **Unlink this phone** in Settings. Unlinking clears the local pairing and sends an authenticated unlink request to the laptop.

## 8. Test the full alarm flow

Before relying on it, test all paths while awake.

1. On laptop dashboard, confirm:

   ```text
   Firebase: connected ✓
   Phone: connected ✓
   ```

2. Set target to:

   ```text
   Both
   ```

3. Set the phone alert mode to **Full panic**.
4. Use the dashboard **Test Raid** button.
5. Confirm:

   ```text
   laptop sound/flash starts
   → Firebase state updates
   → paired phone receives FCM alert
   → phone wake alarm plays/vibrates/displays full screen
   → acknowledge on either device stops the other
   → both enter cooldown
   ```

Then separately test laptop-only, phone-only, Silent mode, quiet hours, auto-silence, vibration off, and flash off.

## 9. Wake behavior

### Android

For critical mode, the paired phone uses high-priority FCM, foreground alarm service, alarm-stream playback, a bounded wake lock, vibration, and a full-screen lock-screen alarm. Phone manufacturers and Android battery policies can still affect delivery; battery exemption and full-screen permission should be enabled.

### Windows

The laptop monitor cannot detect a visual cue while Windows is fully suspended because the process and display are inactive. It can alarm while Windows is running with the display off/locked.

## 10. Troubleshooting

| Problem | Check |
|---|---|
| OCR not working | Install Tesseract, ensure `tesseract` is on PATH, then use **Check OCR engine**. |
| No visual detection | Narrow the selected region, test it locally, check OCR text/image score, and increase/decrease threshold deliberately. |
| Firebase unavailable | Verify database URL, service-account JSON, internet access, and published rules. |
| Pair request remains pending | Ensure Anonymous Authentication is enabled, the phone has internet, the laptop app is open, and the pairing code is from that laptop. |
| Phone does not wake | Verify pairing, FCM/project configuration, notifications, battery exemption, full-screen permission, and phone alert mode. |
| Phone not shown connected | Open the Android app after pairing and allow its foreground monitor to run. |
| Laptop audio missing | Verify bundled WAV assets or choose a custom file in Alarm Settings. |

## Security

- The pairing code contains a private pairing secret. Do not show it to other people.
- Keep the service-account JSON private and outside Git.
- Keep the Firebase project private.
- If a service-account key is exposed, revoke it in Firebase Console and generate a replacement.
- Unlink a phone before selling, resetting, or giving it away.
