# تشغيل محرر على Android دون استضافة

هذه الطريقة تشغّل خادم Python ومنظومة OpenAI Agents SDK داخل الهاتف بواسطة Termux، ولا تحتاج إلى Render أو بطاقة دفع.

## المتطلبات

- هاتف Android 7 أو أحدث.
- تطبيق Termux من F-Droid أو من مستودع Termux الرسمي على GitHub. لا تستخدم النسخة القديمة من Google Play.
- اتصال بالإنترنت عند تثبيت الحزم وعند تشغيل الوكلاء.

## تنزيل المشروع

لأن المستودع خاص، افتحه من تطبيق GitHub أو المتصفح ثم اختر Download ZIP، وفك الضغط. انقل مجلد المشروع إلى مجلد Download في الهاتف.

افتح Termux ونفذ:

```bash
termux-setup-storage
cd ~/storage/downloads/moharrir-agents-main
bash termux-install.sh
```

إن كان اسم المجلد مختلفاً، استعمل اسمه الفعلي بعد `cd ~/storage/downloads/`.

## التشغيل

```bash
cd ~/storage/downloads/moharrir-agents-main
bash termux-run.sh
```

ثم افتح في متصفح الهاتف:

```text
http://127.0.0.1:8000
```

أدخل مفتاح OpenAI داخل واجهة التطبيق. المفتاح لا يكتب في المستودع ولا في ملفات الخادم.

## الإيقاف

```bash
cd ~/storage/downloads/moharrir-agents-main
bash termux-stop.sh
```

## السجل عند الفشل

```bash
tail -n 100 data/termux.log
```

## ملاحظات

- أوقف تحسين البطارية لتطبيق Termux حتى لا يغلق Android الخادم في الخلفية.
- التطبيق متاح على الهاتف نفسه فقط عبر `127.0.0.1`، ولا يكون مكشوفاً للإنترنت.
- هذه الطريقة لا تعمل على iPhone؛ iOS لا يوفر بيئة Python دائمة مماثلة لتشغيل Agents SDK.
