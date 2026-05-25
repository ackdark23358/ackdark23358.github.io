document.addEventListener('DOMContentLoaded', () => {
    const card = document.getElementById('card');
    const scrollContainer = document.querySelector('.scroll-container');
    const resumeSections = document.querySelectorAll('.resume-content section');
    const scrollHint = document.getElementById('scrollHint');
    
    let ticking = false;

    function updateAnimation() {
        // scroll-container의 높이를 기준으로 애니메이션 진행률 계산
        const scrollY = window.scrollY;
        // scroll-container가 끝나는 지점 (sticky가 끝나는 지점)
        const maxScroll = scrollContainer.offsetHeight - window.innerHeight;
        
        // progress는 0에서 1까지만 제한
        const progress = Math.min(Math.max(scrollY / maxScroll, 0), 1);

        // Phase 1 (0.0 ~ 0.5): 명함 뒤집기
        // Phase 2 (0.5 ~ 1.0): 명함 확대

        let rotateX = 10;
        let rotateY = -15;
        let scale = 1;

        if (progress <= 0.5) {
            const flipProgress = progress / 0.5;
            rotateX = 10 * (1 - flipProgress);
            rotateY = -15 + (195 * flipProgress);
            scale = 1;
            card.style.opacity = 1;
        } else {
            const scaleProgress = (progress - 0.5) / 0.5;
            rotateX = 0;
            rotateY = 180;
            
            // 확대 효과 (가속도 곡선 적용하여 점점 빠르게 커지도록)
            const easeScale = scaleProgress * scaleProgress * scaleProgress;
            scale = 1 + (40 * easeScale); // 화면을 덮도록 크게 확대
            
            card.style.opacity = 1;
        }

        // 계산된 속성값을 CSS transform에 적용
        card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(${scale})`;

        if (scrollHint) {
            scrollHint.classList.toggle('is-hidden', scrollY > 24);
        }

        ticking = false;
    }

    // 스크롤 이벤트 리스너 (requestAnimationFrame으로 성능 최적화)
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(updateAnimation);
            ticking = true;
        }
    });

    // 초기 로드 시 한 번 실행하여 초기 상태 세팅
    updateAnimation();

    // 이력서 섹션 스크롤 애니메이션 (Intersection Observer 활용)
    // 화면에 요소가 나타날 때 애니메이션을 트리거하여 스크롤 양에 구애받지 않음
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.2 // 섹션이 20% 보일 때 애니메이션 트리거
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // 한 번 나타난 후에는 계속 보이게 하려면 아래 주석 해제
                // observer.unobserve(entry.target);
            } else {
                // 스크롤을 위로 올렸을 때 다시 애니메이션을 보고 싶다면
                entry.target.classList.remove('visible');
            }
        });
    }, observerOptions);

    resumeSections.forEach(section => {
        observer.observe(section);
    });
});