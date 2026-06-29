# Install fix attempt 4

Проблема: после исправления подписи APK всё равно показывал `Приложение не установлено`.

## Найденная причина

После предыдущей пересборки `resources.arsc` и часть uncompressed entries оказались не выровнены по 4 байта.

Для Android APK это критично: `resources.arsc` должен быть uncompressed и корректно выровнен. Если он не выровнен, установщик может показать только общее сообщение `Приложение не установлено`.

## Что исправлено

Собрана новая тестовая версия:

- file: `KABAN_RUSSIA_16.26.7.1_SIDE_TEST_INSTALL_FIXED.apk`
- package: `com.break.rusdev`
- versionName: `16.26.7.1`
- versionCode: `1184`
- minSdk: `24`
- targetSdk: `34`
- signature: APK Signature Scheme v2
- SHA-256: `b52a5c4e85641c37cd16262e02a7f95b8f34297589d7180cf36d331ee1045cb0`

## Проверки перед выдачей

- ZIP integrity: OK
- AndroidManifest parse: OK
- package: `com.break.rusdev`
- resources.arsc: uncompressed, offset mod 4 = 0
- assets/dexopt/baseline.prof: uncompressed, offset mod 4 = 0
- assets/dexopt/baseline.profm: uncompressed, offset mod 4 = 0
- APK Signature Scheme v2 RSA signature: OK
- APK Signature Scheme v2 content digest: OK

## Почему теперь сборка другая

В этой сборке:

1. Файлы записаны в порядке local headers оригинального APK, а не в порядке central directory.
2. Для uncompressed entries добавлен корректный alignment extra field.
3. Подпись сделана после выравнивания.
4. Старый повреждённый v2-блок не используется.

## Установка

Перед установкой удалить старую тестовую сборку, если она появилась:

```bash
adb uninstall com.break.rusdev
```

Затем установить APK:

```bash
adb install -r KABAN_RUSSIA_16.26.7.1_SIDE_TEST_INSTALL_FIXED.apk
```

Если снова будет отказ, нужен точный код из ADB, потому что обычный установщик Android скрывает причину.
