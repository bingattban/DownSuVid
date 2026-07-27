# وثائق DownSuVid

## المحتويات

- [نظرة عامة](README.md)
- [هندسة التطبيق](ARCHITECTURE.md)
- [واجهة API الداخلية](API.md)

## بناء التطبيق

### المتطلبات

- Python 3.11
- Buildozer
- Android SDK/NDK

### خطوات البناء

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# بناء APK
buildozer android debug

# بناء AAB للإصدار
buildozer android release