# Install fix attempt 3

Проблема: Android показал `Приложение не установлено, так как его пакет поврежден`.

## Причина

В предыдущей v1+v2 сборке APK был целым как ZIP, но блок `APK Signature Scheme v2` был сформирован неправильно: отсутствовала внешняя length-prefixed sequence для списка signer-блоков.

Из-за этого Android видел APK как повреждённый пакет.

## Исправленная сборка

- file: `KABAN_RUSSIA_16.26.7.1_SIDE_TEST_FIXED_v1v2.apk`
- package: `com.break.rusdev`
- versionName: `16.26.7.1`
- versionCode: `1184`
- minSdk: `24`
- targetSdk: `34`
- signature: v1 + fixed v2
- SHA-256: `ff1969902917e4f596870ed781008646f2a3e8d58d594b1c7a1d187b8f060056`

## Проверки

Проверено перед выдачей:

- ZIP integrity: OK
- JAR/v1 signature: OK
- APK Signing Block v2 structure: OK
- v2 RSA signature verification: OK
- v2 content digest verification: OK
- AndroidManifest package: `com.break.rusdev`
- AndroidManifest versionName: `16.26.7.1`
- AndroidManifest versionCode: `1184`

## Установка

Перед установкой удалить старую тестовую сборку, если она частично появилась:

```bash
adb uninstall com.break.rusdev
```

Затем установить:

```bash
adb install -r KABAN_RUSSIA_16.26.7.1_SIDE_TEST_FIXED_v1v2.apk
```

Если установка через файловый менеджер снова не даст подробностей, ADB покажет точный код ошибки.
