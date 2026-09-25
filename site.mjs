// Site pages and languages, shared by the Vite build and tools/check-translations.mjs.
//
// English is served from the site root. Every other language has the same pages under
// /<code>/, for example /ko/work/solar-mlops/. Each translation is a full HTML file in its
// language folder; this file only holds the short interface strings used by the partials.

export const SITE_URL = 'https://azizjonkasimov.github.io'

// Pages that exist in every language. The 404 page is English only.
export const pages = [
  'index.html',
  'work/semantic-search/index.html',
  'work/aws-data-pipeline/index.html',
  'work/solar-mlops/index.html',
  'work/catalog-agent/index.html',
]

// Languages are added one at a time: Korean, German, then Russian. Uzbek and Chinese are next.
// `code` is the URL folder, the hreflang value, and what the browser's languages are matched
// against. `htmlLang` goes in <html lang>. `name` is shown in the language menu, in its own
// language. In `translated`, the part in braces becomes a link to the English version of the page.
export const locales = [
  {
    code: 'en',
    htmlLang: 'en',
    ogLocale: 'en_US',
    name: 'English',
    short: 'EN',
    ui: {
      skip: 'Skip to content',
      home: 'Azizjon Kasimov, home',
      nav: 'Main',
      work: 'Work',
      build: 'How I build',
      experience: 'Experience',
      skills: 'Skills',
      contact: 'Contact',
      language: 'Language',
      email: 'Email',
      imageAlt: 'Azizjon Kasimov, AI/ML Engineer',
      translated: '',
    },
  },
  {
    code: 'ko',
    htmlLang: 'ko',
    ogLocale: 'ko_KR',
    name: '한국어',
    short: 'KO',
    ui: {
      skip: '본문으로 건너뛰기',
      home: 'Azizjon Kasimov, 홈',
      nav: '주요 메뉴',
      work: '프로젝트',
      build: '개발 방식',
      experience: '경력',
      skills: '기술',
      contact: '연락처',
      language: '언어',
      email: '이메일',
      imageAlt: 'Azizjon Kasimov, AI/ML 엔지니어',
      translated: '이 페이지는 {영어 원문}을 번역한 것입니다.',
    },
  },
  {
    code: 'de',
    htmlLang: 'de',
    ogLocale: 'de_DE',
    name: 'Deutsch',
    short: 'DE',
    ui: {
      skip: 'Zum Inhalt springen',
      home: 'Azizjon Kasimov, Startseite',
      nav: 'Hauptmenü',
      work: 'Projekte',
      build: 'Arbeitsweise',
      experience: 'Erfahrung',
      skills: 'Kenntnisse',
      contact: 'Kontakt',
      language: 'Sprache',
      email: 'E-Mail',
      imageAlt: 'Azizjon Kasimov, AI/ML Engineer',
      translated: 'Diese Seite ist eine Übersetzung des {englischen Originals}.',
    },
  },
  {
    code: 'ru',
    htmlLang: 'ru',
    ogLocale: 'ru_RU',
    name: 'Русский',
    short: 'RU',
    ui: {
      skip: 'Перейти к содержимому',
      home: 'Azizjon Kasimov, главная',
      nav: 'Основное меню',
      work: 'Проекты',
      build: 'Как я работаю',
      experience: 'Опыт',
      skills: 'Навыки',
      contact: 'Контакты',
      language: 'Язык',
      email: 'Почта',
      imageAlt: 'Azizjon Kasimov, AI/ML-инженер',
      translated: 'Эта страница — перевод {английского оригинала}.',
    },
  },
]

// Folder path of a page in a language, e.g. ('ko', 'index.html') -> 'ko/index.html'.
export const localizedFile = (code, page) => (code === 'en' ? page : `${code}/${page}`)

// URL path of a page file, e.g. 'ko/work/solar-mlops/index.html' -> '/ko/work/solar-mlops/'.
export const urlPath = (file) => '/' + file.replace(/index\.html$/, '')
