/* ========================================
   iogameguide.com - JavaScript 主文件
   处理导航、搜索、移动端菜单等交互
   ======================================== */

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initSearch();
    initSmoothScroll();
    initScrollEffects();
});

/* ========================================
   移动端汉堡菜单
   ======================================== */
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (!hamburger || !navLinks) return;
    
    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
    
    // 点击导航链接后关闭菜单
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
    
    // 点击页面其他地方关闭菜单
    document.addEventListener('click', function(e) {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        }
    });
}

/* ========================================
   搜索功能
   ======================================== */
function initSearch() {
    const searchInput = document.querySelector('.search-box input');
    if (!searchInput) return;
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.trim();
            if (query) {
                // 跳转到游戏列表页并传递搜索参数
                window.location.href = `games.html?search=${encodeURIComponent(query)}`;
            }
        }
    });
}

/* ========================================
   平滑滚动
   ======================================== */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/* ========================================
   滚动效果
   ======================================== */
function initScrollEffects() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    // 导航栏滚动效果
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        // 添加阴影效果
        if (currentScroll > 50) {
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
        } else {
            navbar.style.boxShadow = 'none';
        }
        
        lastScroll = currentScroll;
    });
    
    // 元素进入视口动画
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // 为游戏卡片添加动画
    document.querySelectorAll('.game-card, .guide-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
}

// 添加淡入动画样式
const style = document.createElement('style');
style.textContent = `
    .fade-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

/* ========================================
   游戏数据（用于动态渲染）
   ======================================== */
const gamesData = [
    {
        id: 'agar-io',
        name: 'Agar.io',
        icon: '🟢',
        iconColor: '#00c853',
        guideCount: 12,
        difficulty: 2,
        tags: ['Multiplayer', 'Cell', 'Growth'],
        description: 'Consume smaller cells to grow, avoid bigger ones.'
    },
    {
        id: 'slither-io',
        name: 'Slither.io',
        icon: '🐍',
        iconColor: '#7c4dff',
        guideCount: 8,
        difficulty: 2,
        tags: ['Snake', 'Multiplayer', 'Arena'],
        description: 'Grow your snake by collecting pellets, outsmart others.'
    },
    {
        id: 'diep-io',
        name: 'Diep.io',
        icon: '🎯',
        iconColor: '#ff5722',
        guideCount: 10,
        difficulty: 3,
        tags: ['Tank', 'Shooting', 'Strategy'],
        description: 'Control a tank, destroy shapes, evolve your build.'
    },
    {
        id: 'paper-io',
        name: 'Paper.io',
        icon: '📄',
        iconColor: '#2196f3',
        guideCount: 6,
        difficulty: 3,
        tags: ['Territory', 'Strategy', 'Grid'],
        description: 'Capture territory by creating enclosed areas.'
    },
    {
        id: 'mope-io',
        name: 'Mope.io',
        icon: '🌊',
        iconColor: '#00bcd4',
        guideCount: 9,
        difficulty: 2,
        tags: ['Evolution', 'Nature', 'Survival'],
        description: 'Evolve from a tiny creature to a top predator.'
    },
    {
        id: 'sandboxels',
        name: 'Sandboxels',
        icon: '🧪',
        iconColor: '#ffeb3b',
        guideCount: 5,
        difficulty: 1,
        tags: ['Simulation', 'Physics', 'Creative'],
        description: 'Physics-based sandbox simulation game.'
    }
];

/* ========================================
   攻略数据（用于动态渲染）
   ======================================== */
const guidesData = [
    {
        id: 'agar-io-beginner-guide',
        title: 'Agar.io Beginner\'s Guide: From Tiny Cell to Giant',
        game: 'Agar.io',
        gameId: 'agar-io',
        date: '2024-01-15',
        readTime: '8 min',
        excerpt: 'Learn the essential strategies to grow your cell and dominate the Agar.io arena.',
        difficulty: 'Beginner'
    },
    {
        id: 'slither-io-boosting',
        title: 'Mastering Boost in Slither.io: Timing and Tactics',
        game: 'Slither.io',
        gameId: 'slither-io',
        date: '2024-01-12',
        readTime: '6 min',
        excerpt: 'The complete guide to using boost strategically without crashing.',
        difficulty: 'Intermediate'
    },
    {
        id: 'diep-io-tanks',
        title: 'Diep.io Tank Builds Tier List 2024',
        game: 'Diep.io',
        gameId: 'diep-io',
        date: '2024-01-10',
        readTime: '12 min',
        excerpt: 'Discover the best tank builds and upgrades for domination.',
        difficulty: 'Advanced'
    }
];

/* ========================================
   渲染游戏卡片
   ======================================== */
function renderGameCard(game) {
    const difficultyDots = Array(5).fill(0).map((_, i) => 
        `<span class="difficulty-dot ${i < game.difficulty ? 'active' : ''}"></span>`
    ).join('');
    
    const tags = game.tags.map(tag => `<span class="tag">${tag}</span>`).join('');
    
    return `
        <a href="guides/${game.id}-guide.html" class="game-card">
            <div class="game-card-header">
                <div class="game-icon" style="background: ${game.iconColor}20; color: ${game.iconColor};">
                    ${game.icon}
                </div>
                <div class="game-info">
                    <h3>${game.name}</h3>
                    <span class="guide-count">${game.guideCount} guides</span>
                </div>
            </div>
            <div class="difficulty">
                ${difficultyDots}
            </div>
            <div class="game-tags">
                ${tags}
            </div>
        </a>
    `;
}

/* ========================================
   渲染攻略卡片
   ======================================== */
function renderGuideCard(guide) {
    return `
        <a href="guides/${guide.id}.html" class="guide-card">
            <div class="guide-thumb">
                <span style="font-size: 2rem;">🎮</span>
            </div>
            <div class="guide-content">
                <h3>${guide.title}</h3>
                <div class="guide-meta">
                    <span>📅 ${guide.date}</span>
                    <span>⏱️ ${guide.readTime}</span>
                </div>
                <p class="guide-excerpt">${guide.excerpt}</p>
            </div>
        </a>
    `;
}

/* ========================================
   导出函数供页面使用
   ======================================== */
window.iogameguide = {
    games: gamesData,
    guides: guidesData,
    renderGameCard: renderGameCard,
    renderGuideCard: renderGuideCard
};
