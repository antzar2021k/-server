# Data-server compatible APK build

Проблема: side-test сборка с package `com.break.rusdev` устанавливалась, но не подключалась к серверу данных.

## Причина

Тестовый package был изменён только для установки рядом со старым приложением. Для реального подключения к backend/data server это может ломать работу, потому что в APK и на стороне сервисов часто завязаны:

- Android package name;
- Firebase provider authorities;
- AppMetrica provider authorities;
- permissions с package-префиксом;
- backend allowlist/signature/package checks;
- Billing/RuStore/Google configs.

Поэтому side-test пакет `com.break.rusdev` подходит только для проверки установки/UI, но не обязательно подходит для подключения к серверу данных.

## Исправленная сборка для проверки сервера

Собрана версия с оригинальным package:

- file: `KABAN_RUSSIA_16.26.7.1_ORIGINAL_PACKAGE_INSTALL_FIXED.apk`
- package: `com.break.russia`
- versionName: `16.26.7.1`
- versionCode: `1184`
- minSdk: `24`
- targetSdk: `34`
- signature: v1 + v2 debug signature
- SHA-256: `2f3017715a46afafe6e703e758754ffb817a525195f4806d5ed881a13396541b`

## Что сохранено

- package: `com.break.russia`
- launcher activity: `com.blackhub.bronline.launcher.activities.MainActivity`
- game activity: `com.blackhub.bronline.game.core.JNIActivity`
- FileProvider authority: `com.break.russia.provider`
- Firebase provider authority: `com.break.russia.firebaseinitprovider`
- AppMetrica authority: `com.break.russia.appmetrica.preloadinfo.retail`
- AndroidX startup authority: `com.break.russia.androidx-startup`

## Что изменено

- versionName: `16.26.7.0` → `16.26.7.1`
- versionCode: `1183` → `1184`
- UI string: `Играть` → `ЗАПУСК`
- UI string: `Настройки` → `ПАРАМЕТРЫ`
- UI string: `Сервер` → `ОНЛАЙН`
- APK перепакован с корректным alignment для uncompressed entries.
- APK подписан debug-ключом для теста.

## Проверки перед выдачей

- ZIP integrity: OK
- AndroidManifest parse: OK
- package: `com.break.russia`
- versionName: `16.26.7.1`
- versionCode: `1184`
- resources.arsc: uncompressed, offset mod 4 = 0
- assets/dexopt/baseline.prof: uncompressed, offset mod 4 = 0
- assets/dexopt/baseline.profm: uncompressed, offset mod 4 = 0
- APK Signature Scheme v2 RSA signature: OK
- APK Signature Scheme v2 content digest: OK

## Важно про установку

Этот APK нельзя установить поверх старого `com.break.russia`, если старый APK подписан другим ключом.

Для теста нужно:

```bash
adb uninstall com.break.russia
adb install -r KABAN_RUSSIA_16.26.7.1_ORIGINAL_PACKAGE_INSTALL_FIXED.apk
```

Если нужен APK, который обновляется поверх старого без удаления, нужен оригинальный release keystore.

## Если сервер всё равно не подключится

Тогда нужно снимать лог:

```bash
adb logcat | grep -iE "break|blackhub|firebase|appmetrica|http|ssl|server|launcher"
```

По логу можно будет понять, что именно не проходит:

- DNS/интернет;
- HTTP/HTTPS;
- SSL/certificate pinning;
- server allowlist;
- неверный endpoint;
- backend проверяет подпись APK;
- backend проверяет versionCode/versionName.
