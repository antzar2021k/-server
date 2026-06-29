# Install fix attempt 2

Проблема: пользователь получил `Приложение не установлено` даже на side-test сборке.

## Вероятная причина

Предыдущая side-test сборка была подписана JAR/v1-подписью. На части устройств/прошивок Android общий установщик может отказать без подробностей, особенно если ожидается APK Signature Scheme v2+.

## Что сделано

Подготовлена новая side-test сборка:

- file: `KABAN_RUSSIA_16.26.7.1_SIDE_TEST_v1v2signed.apk`
- package: `com.break.rusdev`
- versionName: `16.26.7.1`
- versionCode: `1184`
- minSdk: `24`
- targetSdk: `34`
- signature: v1 + v2
- cert/signature algorithm: SHA256withRSA
- cert validity: 2020-01-01 to 2074-10-04
- SHA-256: `d09745e4779f77711c5475d6c89d65634bbe2a5c1e25d5d391d6e5c03b3160d4`

## Что проверить перед установкой

1. Устройство должно быть Android 7.0+ / API 24+, потому что APK имеет `minSdkVersion=24`.
2. Если ранее частично ставилась тестовая сборка `KABAN DEBUG` / `com.break.rusdev`, удалить её перед установкой.
3. Включить установку из неизвестных источников для приложения, из которого открывается APK.
4. Если снова будет ошибка, получить точный код через ADB:

```bash
adb install -r KABAN_RUSSIA_16.26.7.1_SIDE_TEST_v1v2signed.apk
```

Нужен именно код вроде:

- `INSTALL_FAILED_UPDATE_INCOMPATIBLE`
- `INSTALL_FAILED_NO_MATCHING_ABIS`
- `INSTALL_FAILED_OLDER_SDK`
- `INSTALL_PARSE_FAILED_NO_CERTIFICATES`
- `INSTALL_FAILED_INVALID_APK`

Без точного кода Android показывает слишком общий текст `Приложение не установлено`.
