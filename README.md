# Rust Raid Alarm

A local, cross-device raid-alert dashboard for channels you administer. The laptop client monitors one Discord channel with a **Discord application bot**, triggers local sound/flash alerts, observes a shared Firebase Realtime Database state, and records activity. The Android client listens to the same database using a foreground service and can present a local alarm.

## Important safety and platform boundaries

This repository intentionally does **not** implement Discord self-bots, accept Discord user tokens, scrape authorization headers, add timing jitter to evade platform detection, or automate Snapchat/Discord messages through Accessibility Services. User tokens are account passwords and Discord prohibits automated user accounts. Those features are unsafe and violate platform rules.

Use a dedicated Discord application bot with read access only to the one alert channel. The bot implementation has no send, reaction, command, or mutation code. Phone sharing is user initiated through Android's share sheet.

## Requirements

- Windows 10/11 and Python 3.11+
- An Android 8.0+ device and Android Studio
- A Discord server/channel you administer, plus a Discord application bot
- A Firebase project with Realtime Database

## Discord setup (compliant bot)

1. Open the [Discord Developer Portal](https://discord.com/developers/applications), create an application, then create a bot.
2. Enable the **Message Content Intent** only if message-content matching is required.
3. Generate an OAuth2 URL with `bot` scope and invite the bot to your server.
4. Give it only **View Channel** and **Read Message History** permissions in the alert channel. Do not grant send-message permissions.
5. Copy the bot token from the Bot page and the channel ID from Discord Developer Mode.
6. Enter these in the laptop setup wizard. Never share any token.

The configured optional user ID is used only for matching a mention in that same channel. Every other channel is ignored.

## Firebase setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com).
2. Create a Realtime Database. Use authenticated rules in `firebase/database_rules.json`; do not leave production data in test mode.
3. For the laptop, create a service account key and paste its JSON and database URL in **Settings → Integrations**. Treat this JSON as a secret.
4. For Android, register package `com.rustraid`, download `google-services.json`, and place it at `android_app/app/google-services.json` (this file is intentionally not tracked).
5. Publish the database rules after adapting them to your Firebase Authentication model.

Shared paths are `raid_alarm`, `settings`, `app_meta`, and `activity_log`.

## Laptop setup

```powershell
cd laptop_app
py -3.11 -m pip install -r requirements.txt
py -3.11 main.py
```

The first-run disclosure must be accepted. The wizard saves settings locally in `laptop_app/config.json`. Configure Firebase from Settings if it was skipped. Put licensed WAV assets in `laptop_app/assets/sounds/`; the app remains operational without them. Run `build.bat` on Windows to create a PyInstaller build.

### Alert behavior

- A qualifying mention in the single configured channel triggers the selected laptop preset unless cooldown is active.
- Quiet hours force a silent local alert.
- Acknowledge stops local audio/flash and starts cooldown; **Raid Over** ends cooldown immediately.
- Firebase writes make state available to connected devices. The client fails closed when Firebase is unavailable.

## Android build

1. Install Android Studio and open `android_app`.
2. Add your untracked `android_app/app/google-services.json`.
3. Let Gradle sync and choose **Build → Build APK(s)**.
4. Install the debug APK on your Android device.

The phone's foreground service monitors Firebase while Android permits it. Grant notifications, vibration, and battery-optimization exemptions through normal Android settings if requested. Alarm audio uses the alarm stream; device policy, DND configuration, and OEM battery controls can still limit behavior.

## Troubleshooting

- **Discord disconnected:** check the bot token, channel ID, gateway intents, and that the bot can view exactly the configured channel.
- **Firebase unavailable:** confirm database URL, service-account JSON, network access, and rules.
- **No Android events:** verify `google-services.json`, Firebase project match, notifications, and foreground-service status.
- **No sound:** add licensed audio files to the stated folders and verify OS media permissions.

## Privacy

Keep `config.json`, Firebase service-account files, and `google-services.json` out of source control. The app has no analytics and does not send Discord messages or control third-party apps.
