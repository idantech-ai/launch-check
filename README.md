<div dir="rtl">

# launch-check — בדיקות לפני עלייה לאוויר

סקיל ל-Claude Code שבודק אתר או מערכת שבניתם עם AI **לפני** שהם עולים לאוויר,
ומוציא דוח אחד בעברית לפי חומרה. **הוא לא משנה שום קובץ עד שאתם מאשרים.**

מה נבדק:

| # | בדיקה |
|---|---|
| 1 | אבטחה — הרשאות בצד השרת, סיסמאות, SQL injection, XSS, הגבלת ניסיונות התחברות |
| 2 | נגישות — WCAG 2.1 AA / ת"י 5568: ניגודיות, מקלדת, תוויות, דיאלוגים |
| 3 | מדיניות פרטיות **מול מה שהקוד באמת אוסף** (פיקסלים, אנליטיקס, טפסים, עוגיות) |
| 4 | טפסים שבאמת שולחים (ולא רק מציגים "תודה") |
| 5 | הצהרת נגישות |
| 6 | מובייל, RTL ועיצוב גנרי של AI |
| 7 | מהירות טעינה |
| 8 | SEO ותצוגה בשיתוף בוואטסאפ |
| 9 | קישורים שבורים |
| 10 | מפתחות API חשופים — בקוד, בבילד וב**היסטוריית git** |

## התקנה

**אפשרות 1 — כפלאגין (מומלץ):** בתוך Claude Code:

```
/plugin marketplace add idantech-ai/launch-check
/plugin install launch-check@idantech
```

**אפשרות 2 — ידנית:** מעתיקים את התיקייה `plugins/launch-check/skills/launch-check`
אל `~/.claude/skills/` (לכל הפרויקטים) או אל `.claude/skills/` בתוך פרויקט אחד.

## שימוש

פותחים את Claude Code בתיקיית הפרויקט וכותבים:

```
/launch-check
```

או רק תחום אחד: `/launch-check security` · `accessibility` · `privacy` · `design` · `quality`

אפשר גם פשוט לכתוב "תבדוק את האתר לפני שאני מעלה אותו".

## לפני שאתם מתקינים — תבדקו אותו

סקיל הוא תוכנה שקלוד מציית לה, אז אל תסמכו עליי — תקראו את הקבצים. הכל כאן גלוי:

- `SKILL.md` — ההוראות לקלוד
- `references/` — מה בודקים בכל תחום
- `scripts/` — שלושה סקריפטים בפייתון, **בלי תלויות, בלי רשת, קריאה בלבד**:
  `scan_secrets.py` (מפתחות וסודות, מוצגים מוסתרים), `static_checks.py` (HTML/CSS), `contrast.py` (ניגודיות + גוון חלופי מאותו צבע)

הסקיל **לא מושך שום תוכן מהאינטרנט** בזמן ריצה. כלים חיצוניים (Lighthouse, axe, npm audit)
רצים רק אחרי שקלוד מבקש מכם אישור.

## עיצוב — Impeccable

לבדיקות עיצוב מעמיקות הסקיל משתמש ב-[Impeccable](https://impeccable.style) של Paul Bakaus
(קוד פתוח, Apache 2.0) **אם הוא כבר מותקן אצלכם**. הוא לא מותקן אוטומטית.
שימו לב ש-Impeccable אוסף נתוני שימוש, ואפשר לכבות: `npx impeccable telemetry off`.

## חשוב לדעת

בדיקה אוטומטית ובדיקת AI הן קו ראשון חזק, **לא אישור רשמי**. עמידה בתקן הנגישות
נקבעת על ידי יועץ נגישות מורשה, ומדיניות פרטיות לעסק עם מידע רגיש כדאי לעבור עם עורך דין.

## מדריכים מלאים

- [10 בדיקות לפני עלייה לאוויר](https://idantech.co.il/guides/launch-checks)
- [אבטחה מהפקודה הראשונה](https://idantech.co.il/guides/security-first-prompt)
- [נגישות עם קלוד](https://idantech.co.il/guides/accessibility-claude)
- [מדיניות פרטיות עם AI](https://idantech.co.il/guides/privacy-policy-ai)
- [ככה קלוד מפסיק לעצב כמו AI](https://idantech.co.il/guides/claude-design)

נבנה על ידי [עידן עייש — IdanTech](https://idantech.co.il) · רישיון MIT

</div>
