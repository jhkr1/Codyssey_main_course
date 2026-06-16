const GITHUB_USERNAME = 'jhkr1';
const PROJECT_LIMIT = 6;
const SCROLL_TOP_THRESHOLD = 300;
const HEADER_THRESHOLD = 60;
const OBSERVER_THRESHOLD = 0.2;

// 화면을 결정하는 값들을 한 곳에서 관리한다.
const state = {
  theme: 'light',
  isMenuOpen: false,
  projects: [],
  projectStatus: 'idle',
  selectedLanguage: 'all',
  formErrors: {},
};

// HTML에서 JavaScript가 사용할 DOM 요소들을 미리 선택한다.
const elements = {
  root: document.documentElement,
  body: document.body,
  header: document.querySelector('[data-header]'),
  menuToggle: document.querySelector('[data-menu-toggle]'),
  navPanel: document.querySelector('[data-nav-panel]'),
  navLinks: document.querySelectorAll('.nav-link, .brand, .hero-actions a'),
  themeToggle: document.querySelector('[data-theme-toggle]'),
  themeIcon: document.querySelector('[data-theme-icon]'),
  themeLabel: document.querySelector('[data-theme-label]'),
  scrollTop: document.querySelector('[data-scroll-top]'),
  projectStatus: document.querySelector('[data-project-status]'),
  projectList: document.querySelector('[data-project-list]'),
  retryButton: document.querySelector('[data-retry-button]'),
  filterBar: document.querySelector('[data-filter-bar]'),
  contactForm: document.querySelector('[data-contact-form]'),
  formSuccess: document.querySelector('[data-form-success]'),
  revealItems: document.querySelectorAll('.reveal'),
};

// 페이지가 처음 로드되면 실행되는 시작 함수다.
const init = () => {
  restoreTheme();
  bindEvents();
  observeSections();
  handleScroll();
  loadProjects();
};

// 사용자 이벤트를 각 기능 함수와 연결한다.
const bindEvents = () => {
  elements.menuToggle.addEventListener('click', toggleMenu);
  elements.themeToggle.addEventListener('click', toggleTheme);
  elements.scrollTop.addEventListener('click', scrollToTop);
  elements.retryButton.addEventListener('click', loadProjects);
  elements.contactForm.addEventListener('submit', handleFormSubmit);
  elements.contactForm.addEventListener('input', handleFormInput);
  elements.filterBar.addEventListener('click', handleFilterClick);
  window.addEventListener('scroll', handleScroll);

  elements.navLinks.forEach((link) => {
    link.addEventListener('click', closeMenu);
  });
};

// 저장된 테마가 있으면 불러오고, 없으면 시스템 다크 모드 설정을 참고한다.
const restoreTheme = () => {
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  state.theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  renderTheme();
};

// 다크 모드와 라이트 모드를 번갈아 전환한다.
const toggleTheme = () => {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('theme', state.theme);
  renderTheme();
};

// theme 상태를 실제 html 속성과 버튼 텍스트에 반영한다.
const renderTheme = () => {
  const isDark = state.theme === 'dark';

  elements.root.dataset.theme = state.theme;
  elements.themeIcon.textContent = isDark ? '☀' : '☾';
  elements.themeLabel.textContent = isDark ? 'Light' : 'Dark';
  elements.themeToggle.setAttribute(
    'aria-label',
    isDark ? '라이트 모드로 변경' : '다크 모드로 변경',
  );
};

// 모바일 메뉴의 열림 상태를 반대로 바꾼다.
const toggleMenu = () => {
  state.isMenuOpen = !state.isMenuOpen;
  renderMenu();
};

// 메뉴 링크를 클릭했을 때 모바일 메뉴를 닫는다.
const closeMenu = () => {
  state.isMenuOpen = false;
  elements.navPanel.classList.remove('active');
  elements.body.classList.remove('menu-open');
  elements.menuToggle.setAttribute('aria-expanded', 'false');
  elements.menuToggle.setAttribute('aria-label', '메뉴 열기');
};

// isMenuOpen 상태에 따라 메뉴 패널과 body 클래스를 업데이트한다.
const renderMenu = () => {
  elements.navPanel.classList.toggle('active', state.isMenuOpen);
  elements.body.classList.toggle('menu-open', state.isMenuOpen);
  elements.menuToggle.setAttribute('aria-expanded', String(state.isMenuOpen));
  elements.menuToggle.setAttribute(
    'aria-label',
    state.isMenuOpen ? '메뉴 닫기' : '메뉴 열기',
  );
};

// 스크롤 위치에 따라 상단 버튼과 헤더 스타일을 바꾼다.
const handleScroll = () => {
  const shouldShowTop = window.scrollY > SCROLL_TOP_THRESHOLD;
  const shouldChangeHeader = window.scrollY > HEADER_THRESHOLD;

  elements.scrollTop.classList.toggle('visible', shouldShowTop);
  elements.header.classList.toggle('scrolled', shouldChangeHeader);
};

// 스크롤 탑 버튼을 클릭하면 페이지 맨 위로 부드럽게 이동한다.
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  });
};

// 섹션이 화면에 들어오면 visible 클래스를 붙여 스크롤 애니메이션을 실행한다.
const observeSections = () => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: OBSERVER_THRESHOLD,
    },
  );

  elements.revealItems.forEach((item) => observer.observe(item));
};

// GitHub API에서 저장소를 가져오고, 화면에 필요한 형태로 가공한다.
const loadProjects = async () => {
  state.projectStatus = 'loading';
  state.projects = [];
  renderProjects();

  try {
    const response = await fetch(`https://api.github.com/users/${GITHUB_USERNAME}/repos`);

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }

    const data = await response.json();

    state.projects = data
      .filter(({ fork }) => !fork)
      .sort((firstRepo, secondRepo) => {
        const firstDate = new Date(firstRepo.pushed_at).getTime();
        const secondDate = new Date(secondRepo.pushed_at).getTime();

        return secondDate - firstDate;
      })
      .slice(0, PROJECT_LIMIT)
      .map(({ name, description, html_url, homepage, language, stargazers_count }) => ({
        name,
        description,
        url: html_url,
        homepage,
        language: language || '기타',
        stars: stargazers_count,
      }));

    state.projectStatus = state.projects.length > 0 ? 'success' : 'empty';
    state.selectedLanguage = 'all';
  } catch (error) {
    console.error(error);
    state.projectStatus = 'error';
  }

  renderFilters();
  renderProjects();
};

// 프로젝트 언어 목록을 바탕으로 필터 버튼을 다시 그린다.
const renderFilters = () => {
  const languages = [...new Set(state.projects.map(({ language }) => language))];
  const filterButtons = ['all', ...languages]
    .map((language) => {
      const label = language === 'all' ? 'All' : language;
      const isActive = state.selectedLanguage === language;

      return `
        <button class="filter-button ${isActive ? 'active' : ''}" type="button" data-filter="${language}">
          ${label}
        </button>
      `;
    })
    .join('');

  elements.filterBar.innerHTML = filterButtons;
};

// 필터 버튼을 클릭하면 선택 언어 상태를 바꾸고 프로젝트 목록을 다시 그린다.
const handleFilterClick = (event) => {
  const button = event.target.closest('[data-filter]');

  if (!button) {
    return;
  }

  state.selectedLanguage = button.dataset.filter;
  renderFilters();
  renderProjects();
};

// 현재 선택된 언어 필터에 맞는 프로젝트만 반환한다.
const getVisibleProjects = () => {
  if (state.selectedLanguage === 'all') {
    return state.projects;
  }

  return state.projects.filter(({ language }) => language === state.selectedLanguage);
};

// API에서 받은 문자열이 HTML로 실행되지 않도록 특수 문자를 변환한다.
const escapeHTML = (value) =>
  String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

// projectStatus 상태에 따라 로딩, 에러, 빈 상태, 성공 UI를 렌더링한다.
const renderProjects = () => {
  elements.projectList.innerHTML = '';

  if (state.projectStatus === 'loading') {
    elements.projectStatus.textContent = '프로젝트를 불러오는 중입니다...';
    return;
  }

  if (state.projectStatus === 'error') {
    elements.projectStatus.textContent = '프로젝트를 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.';
    return;
  }

  if (state.projectStatus === 'empty') {
    elements.projectStatus.textContent = '표시할 프로젝트가 없습니다.';
    return;
  }

  const visibleProjects = getVisibleProjects();

  if (visibleProjects.length === 0) {
    elements.projectStatus.textContent = '선택한 언어의 프로젝트가 없습니다.';
    return;
  }

  elements.projectStatus.textContent = `최신 프로젝트 ${visibleProjects.length}개를 표시하고 있습니다.`;
  elements.projectList.innerHTML = visibleProjects.map(createProjectCard).join('');
};

// 프로젝트 객체 하나를 카드 HTML 문자열로 변환한다.
const createProjectCard = ({ name, description, url, homepage, language, stars }) => {
  const safeName = escapeHTML(name);
  const safeDescription = escapeHTML(description || '저장소 설명이 아직 작성되지 않았습니다.');
  const safeUrl = escapeHTML(url);
  const safeHomepage = homepage ? escapeHTML(homepage) : '';
  const safeLanguage = escapeHTML(language);
  const safeStars = escapeHTML(stars);

  return `
    <article class="project-card">
      <h3>${safeName}</h3>
      <p>${safeDescription}</p>
      <div class="project-meta" aria-label="${safeName} 저장소 정보">
        <span class="project-badge">${safeLanguage}</span>
        <span class="project-badge">★ ${safeStars}</span>
      </div>
      <a class="project-link" href="${safeUrl}" target="_blank" rel="noreferrer">GitHub에서 보기</a>
      ${
        safeHomepage
          ? `<a class="project-link" href="${safeHomepage}" target="_blank" rel="noreferrer">배포 페이지 보기</a>`
          : ''
      }
    </article>
  `;
};

// 입력 중에도 폼 오류 메시지를 즉시 갱신한다.
const handleFormInput = (event) => {
  const { name } = event.target;

  if (!['name', 'email', 'message'].includes(name)) {
    return;
  }

  const formData = new FormData(elements.contactForm);
  state.formErrors = validateForm(formData);
  elements.formSuccess.textContent = '';
  renderFormErrors();
};

// 폼 제출 시 새로고침을 막고 입력값을 검사한다.
const handleFormSubmit = (event) => {
  event.preventDefault();

  const formData = new FormData(elements.contactForm);
  state.formErrors = validateForm(formData);
  renderFormErrors();

  if (Object.keys(state.formErrors).length > 0) {
    elements.formSuccess.textContent = '';
    return;
  }

  elements.formSuccess.textContent = '메시지가 확인되었습니다. 실제 전송 연동은 다음 단계에서 추가할 수 있습니다.';
  elements.contactForm.reset();
};

// 이름, 이메일, 메시지 값을 검사하고 에러 객체를 반환한다.
const validateForm = (formData) => {
  const values = {
    name: String(formData.get('name')).trim(),
    email: String(formData.get('email')).trim(),
    message: String(formData.get('message')).trim(),
  };
  const errors = {};
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!values.name) {
    errors.name = '이름을 입력해 주세요.';
  }

  if (!values.email) {
    errors.email = '이메일을 입력해 주세요.';
  } else if (!emailPattern.test(values.email)) {
    errors.email = '올바른 이메일 형식으로 입력해 주세요.';
  }

  if (!values.message) {
    errors.message = '메시지를 입력해 주세요.';
  }

  return errors;
};

// formErrors 상태를 각 입력 필드 아래의 에러 메시지에 반영한다.
const renderFormErrors = () => {
  const fields = ['name', 'email', 'message'];

  fields.forEach((field) => {
    const errorElement = document.querySelector(`[data-error-for="${field}"]`);
    errorElement.textContent = state.formErrors[field] || '';
  });
};

init();
