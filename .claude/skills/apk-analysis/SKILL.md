---
name: apk-analysis
description: Verify and decompile the MyRenault Android app (com.renault.myrenault.one.fr) to check API endpoints, headers, OIDC settings or featureId semantics against the official app. Use when reviewing docs or PRs that cite the APK, or when asked what the app does for a given endpoint or featureId.
---

# MyRenault APK analysis

Everything lives in `.apk_analysis/` at the repo root (git-ignored). Never
commit APKs or decompiled sources.

## 1. Get the XAPK

Ask the user to download the XAPK (e.g. from APKCombo) into `.apk_analysis/`.

Always run `sha256sum` and compare with any hash quoted in the docs or the PR.
A mismatch means you are not looking at the same build.

## 2. Decompile

Extract the XAPK, then run jadx on the main `com.renault.myrenault.one.fr.apk`
(the `config.*.apk` splits hold only native libs and resources).

- Install Java if missing: `sudo apt-get install -y openjdk-21-jre-headless`.
- jadx is expected at `.apk_analysis/jadx/bin/jadx`; if missing, unzip a
  release from https://github.com/skylot/jadx/releases there.
- Limit memory, or the run dies on WSL or small containers:

```bash
JAVA_OPTS="-Xmx5g" .apk_analysis/jadx/bin/jadx -j 4 --no-res --show-bad-code \
  -d .apk_analysis/src-$V .apk_analysis/v$V/com.renault.myrenault.one.fr.apk
```

Run it in the background; it takes about 30 minutes for ~37k files. The run
ends with `ERROR - finished with errors, count: ~620` and exit code 3. That is
normal: some methods don't decompile cleanly.

For string-only checks (no decompilation), `strings` on the `classes*.dex`
files is enough, e.g. OIDC scopes or remote-config keys.

## 3. Where things are

- App code: `com/accenture/myrenault/`, `com/renault/` (e.g. `com/renault/zepass`
  for Plug & Charge) and the obfuscated `defpackage/`. Search all three.
- featureId to feature flags: `com.renault.core.utils.ServiceMappingConfig`.
  Obfuscated into `defpackage/`; find it with
  `grep -rl 'ServiceMappingConfig' defpackage`. In 6.13.4 jadx keeps the field
  names. In 6.14.2 they are obfuscated, but the original names are in the
  class's `@Metadata(d2 = {...})`, in field order.
- `POST /state` request: `GetSohBatteryWithMileageUseCase`.
- Map layers: `MapSelectionUiMapper` builds `CarMapUiModel`.
- Remote-config defaults: `res/xml/remote_config_defaults.xml` (binary XML).
  Many flags, e.g. `SOH_UID_list`, are server-only.

## 4. Pitfalls

- **Inlined constants.** jadx shows some integer literals as unrelated library
  constants of the same value: 202/204 as OneTrust
  `OTUIDisplayReasonCode.UIShownCode.PC_SHOWN_*`, and 344/364/952/953/955/973
  as Contentsquare `Currencies.*`. Before saying an id is unused, look for
  `public static final int X = <id>;` and search for `.X` too.
- **`@Metadata` noise.** Kotlin metadata strings match almost any grep; filter
  out `@Metadata` lines.
- **Partial searches.** Say "not found in <packages searched>", never just
  "not found", and check `com/renault/` before concluding.
- **Version drift.** Before calling something a change between versions,
  decompile both and compare (e.g. the `ServiceMappingConfig` id lists).
