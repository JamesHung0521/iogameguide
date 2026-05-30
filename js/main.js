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
        id: 'defend-io',
        name: 'Defend.io',
        icon: '🏰',
        iconColor: '#4caf50',
        guideCount: 1,
        difficulty: 3,
        tags: ['Tower Defense', 'Strategy', 'Unity'],
        description: 'Stop waves of enemies with strategic tower placement.'
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
        id: 'hole-io',
        name: 'Hole.io',
        icon: '🕳️',
        iconColor: '#1a1a2e',
        guideCount: 3,
        difficulty: 1,
        tags: ['Swallow', 'City', 'Growth'],
        description: 'Control a black hole that swallows cities and objects.'
    },
    {
        id: 'krunker-io',
        name: 'Krunker.io',
        icon: '🎯',
        iconColor: '#ff6b35',
        guideCount: 4,
        difficulty: 4,
        tags: ['FPS', 'Shooter', 'Combat'],
        description: 'Fast-paced first-person shooter .io game.'
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
    },
    {
        id: 'surviv-io',
        name: 'Surviv.io',
        icon: '🎮',
        iconColor: '#ff9800',
        guideCount: 3,
        difficulty: 3,
        tags: ['Battle Royale', 'Shooter', 'Survival'],
        description: '2D battle royale with weapons and tactics.'
    },
    {
        id: 'bloxd-io',
        name: 'Bloxd.io',
        icon: '🧱',
        iconColor: '#e91e63',
        guideCount: 2,
        difficulty: 3,
        tags: ['Building', 'PvP', 'Parkour'],
        description: 'Minecraft-style building and combat game.'
    },
    {
        id: 'crazysteve-io',
        name: 'CrazySteve.io',
        icon: '🧱',
        iconColor: '#4caf50',
        guideCount: 1,
        difficulty: 3,
        tags: ['Building', 'Battle Royale', 'FPS'],
        description: 'Minecraft-style block building battle royale shooter.'
    },
    {
        id: 'curser-io',
        name: 'Curser.io',
        icon: '🖱️',
        iconColor: '#9c27b0',
        guideCount: 1,
        difficulty: 2,
        tags: ['Survival', 'Cursor', 'Strategy'],
        description: 'Navigate and survive the cursor wars in this unique browser game.'
    },
    {
        id: 'blumgi-rocket',
        name: 'Blumgi Rocket',
        icon: '🚀',
        iconColor: '#ff6b35',
        guideCount: 1,
        difficulty: 2,
        tags: ['Platform', 'Physics', 'Rocket'],
        description: 'Physics-based rocket platformer with precision landing.'
    },
    {
        id: 'shell-shockers',
        name: 'Shell Shockers',
        icon: '🥚',
        iconColor: '#ffeb3b',
        guideCount: 2,
        difficulty: 3,
        tags: ['FPS', 'Shooter', 'Egg'],
        description: 'First-person egg shooter combat game.'
    },
    {
        id: 'venge-io',
        name: 'Venge.io',
        icon: '💀',
        iconColor: '#9c27b0',
        guideCount: 2,
        difficulty: 4,
        tags: ['FPS', 'Shooter', 'Class'],
        description: 'Tactical FPS with class-based combat.'
    },
    {
        id: 'taming-io',
        name: 'Taming.io',
        icon: '🦎',
        iconColor: '#4caf50',
        guideCount: 2,
        difficulty: 2,
        tags: ['Pets', 'Building', 'Survival'],
        description: 'Tame pets and build your base.'
    },
    {
        id: 'yohoho-io',
        name: 'Yohoho.io',
        icon: '🏴‍☠️',
        iconColor: '#795548',
        guideCount: 2,
        difficulty: 2,
        tags: ['Pirate', 'Battle', 'Collect'],
        description: 'Battle royale with pirate themes.'
    },
    {
        id: 'evowars-io',
        name: 'EvoWars.io',
        icon: '⚔️',
        iconColor: '#f44336',
        guideCount: 2,
        difficulty: 2,
        tags: ['Evolution', 'Combat', 'Sword'],
        description: 'Evolution and combat game with weapons.'
    },
    {
        id: 'skribbl-io',
        name: 'Skribbl.io',
        icon: '✏️',
        iconColor: '#3f51b5',
        guideCount: 2,
        difficulty: 1,
        tags: ['Drawing', 'Party', 'Guessing'],
        description: 'Drawing and guessing party game.'
    },
    {
        id: 'zombsroyale-io',
        name: 'ZombsRoyale.io',
        icon: '💣',
        iconColor: '#607d8b',
        guideCount: 2,
        difficulty: 3,
        tags: ['Battle Royale', 'Zombie', 'Shooter'],
        description: 'Top-down battle royale shooter.'
    },
    {
        id: 'gartic-io',
        name: 'Gartic.io',
        icon: '🎨',
        iconColor: '#00bcd4',
        guideCount: 2,
        difficulty: 1,
        tags: ['Drawing', 'Party', 'Guessing'],
        description: 'Drawing and guessing multiplayer game.'
    },
    {
        id: 'wings-io',
        name: 'Wings.io',
        icon: '✈️',
        iconColor: '#2196f3',
        guideCount: 2,
        difficulty: 2,
        tags: ['Flight', 'Combat', 'Aircraft'],
        description: 'Aerial combat with planes and dogfights.'
    },
    {
        id: 'moomoo-io',
        name: 'MooMoo.io',
        icon: '🐄',
        iconColor: '#8d6e63',
        guideCount: 2,
        difficulty: 2,
        tags: ['Survival', 'Building', 'Base'],
        description: 'Survival sandbox with base building.'
    },
    {
        id: 'smashkarts-io',
        name: 'SmashKarts.io',
        icon: '🏎️',
        iconColor: '#ff6b35',
        guideCount: 1,
        difficulty: 2,
        tags: ['Kart', 'Combat', 'Battle'],
        description: 'Multiplayer kart battle with weapons and power-ups.'
    },
    {
        id: 'angry-worms-io',
        name: 'Angry Worms.io',
        icon: '🐛',
        iconColor: '#e53935',
        guideCount: 1,
        difficulty: 2,
        tags: ['Snake', 'Worm', 'Multiplayer'],
        description: 'Grow your worm and make opponents crash into you.'
    },
    {
        id: 'blumgi-rocket',
        name: 'Blumgi Rocket',
        icon: '🚀',
        iconColor: '#ff9800',
        guideCount: 1,
        difficulty: 2,
        tags: ['Rocket', 'Physics', 'Platform'],
        description: 'Launch yourself through obstacle courses using rocket boosters.'
    },
    {
        id: 'brutalmania-io',
        name: 'BrutalMania.io',
        icon: '⚔️',
        iconColor: '#dc2626',
        guideCount: 1,
        difficulty: 2,
        tags: ['Fighting', 'Action', 'Arena'],
        description: 'Gladiator arena combat with various weapons and upgrades.'
    },
    {
        id: 'swordz-io',
        name: 'Swordz.io',
        icon: '⚔️',
        iconColor: '#c0c0c0',
        guideCount: 1,
        difficulty: 2,
        tags: ['Sword', 'Combat', 'Medieval'],
        description: 'Medieval sword fighting arena with dash and swing mechanics.'
    },
    {
        id: 'medieval-io',
        name: 'Medieval.io',
        icon: '🏰',
        iconColor: '#8b4513',
        guideCount: 1,
        difficulty: 3,
        tags: ['RPG', 'Action', 'Battle'],
        description: '8-player real-time battle arena with hero collection.'
    },
    {
        id: 'defly-io',
        name: 'Defly.io',
        icon: '🚁',
        iconColor: '#10b981',
        guideCount: 1,
        difficulty: 3,
        tags: ['Territory', 'Helicopter', 'Strategy'],
        description: 'Helicopter combat with territory capture and base building.'
    },
    {
        id: 'dogod-io',
        name: 'Dogod.io',
        icon: '🦎',
        iconColor: '#f59e0b',
        guideCount: 1,
        difficulty: 2,
        tags: ['Evolution', 'Survival', 'Food Chain'],
        description: 'Climb the food chain from tiny creature to apex predator.'
    },
    {
        id: 'angry-worms-io',
        name: 'Angry Worms.io',
        icon: '🐛',
        iconColor: '#ef4444',
        guideCount: 1,
        difficulty: 2,
        tags: ['Worm', 'Slither', 'Arena'],
        description: 'Slither and grow your worm, trap opponents, dominate the leaderboard.'
    },
    {
        id: 'repuls-io',
        name: 'Repuls.io',
        icon: '🔫',
        iconColor: '#10b981',
        guideCount: 1,
        difficulty: 3,
        tags: ['FPS', 'Shooter', 'Combat'],
        description: 'Fast-paced FPS arena shooter with unique repulsion launcher mechanics.'
    },
    {
        id: 'spawner-io',
        name: 'Spawner.io',
        icon: '🎯',
        iconColor: '#f59e0b',
        guideCount: 1,
        difficulty: 2,
        tags: ['Survival', 'Building', 'Tower Defense'],
        description: 'Spawn blocks, build defenses, and survive endless enemy waves.'
    },
    {
        id: 'starblast-io',
        name: 'Starblast.io',
        icon: '🚀',
        iconColor: '#8b5cf6',
        guideCount: 1,
        difficulty: 3,
        tags: ['Space', 'Shooter', 'Upgrade'],
        description: 'Pilot spaceships, mine asteroids for crystals, upgrade your vessel, and engage in epic space battles.'
    },
    {
        id: 'gulper-io',
        name: 'Gulper.io',
        icon: '🐍',
        iconColor: '#10b981',
        guideCount: 1,
        difficulty: 2,
        tags: ['Snake', 'Growth', 'Arena'],
        description: 'Control a gulper creature, swallow food and smaller players to grow, dominate the arena.'
    }
];

/* ========================================
   攻略数据（用于动态渲染）
   ======================================== */
const guidesData = [
    {
        id: 'diep-io-guide',
        title: 'Diep.io Complete Guide: Master Tank Combat & Upgrades',
        game: 'Diep.io',
        gameId: 'diep-io',
        date: '2026-05-27',
        readTime: '16 min',
        excerpt: 'Master tank combat, upgrade paths, best builds for every class, and dominate the battlefield in Diep.io.',
        difficulty: 'Intermediate'
    },
    {
        id: 'defly-io-guide',
        title: 'Defly.io Guide: Build, Defend & Conquer',
        game: 'Defly.io',
        gameId: 'defly-io',
        date: '2026-05-20',
        readTime: '9 min',
        excerpt: 'Master territory control, helicopter combat, defensive building, and top strategies to dominate the leaderboard.',
        difficulty: 'Beginner'
    },
    {
        id: 'blumgi-rocket-guide',
        title: 'Blumgi Rocket Guide: Launch, Fly & Land Perfectly',
        game: 'Blumgi Rocket',
        gameId: 'blumgi-rocket',
        date: '2026-05-14',
        readTime: '9 min',
        excerpt: 'Master launch mechanics, trajectory prediction, boost management, and perfect landing techniques.',
        difficulty: 'Beginner'
    },
        {
        id: 'brutalmania-io-guide',
        title: 'BrutalMania.io Guide: Arena Combat Tips & Weapon Strategy',
        game: 'BrutalMania.io',
        gameId: 'brutalmania-io',
        date: '2026-05-15',
        readTime: '9 min',
        excerpt: 'Master arena combat tactics, weapon selection, movement strategies, and dominate the battleground.',
        difficulty: 'Beginner'
    },
    {
        id: 'swordz-io-guide',
        title: 'Swordz.io Complete Guide: Master Medieval Combat',
        game: 'Swordz.io',
        gameId: 'swordz-io',
        date: '2026-05-16',
        readTime: '10 min',
        excerpt: 'Master sword combat, dash mechanics, positioning, and climbing the leaderboard.',
        difficulty: 'Beginner'
    },
    {
        id: 'medieval-io-guide',
        title: 'Medieval.io Complete Guide: Battle Strategies & Hero Guide',
        game: 'Medieval.io',
        gameId: 'medieval-io',
        date: '2026-05-16',
        readTime: '11 min',
        excerpt: 'Dominate the 8-player arena with hero selection, army management, and advanced tactics.',
        difficulty: 'Beginner'
    },
    {
        id: 'agar-io-advanced-guide',
        title: 'Agar.io Advanced Guide: Pro Split Tricks & Late Game Strategy',
        game: 'Agar.io',
        gameId: 'agar-io',
        date: '2026-05-14',
        readTime: '10 min',
        excerpt: 'Master pro split tricks, micro-techniques, late game dominance, and high-level strategies.',
        difficulty: 'Advanced'
    },
    {
        id: 'angry-worms-io-guide',
        title: 'Angry Worms.io Guide: Master the Slither-Style Arena',
        game: 'Angry Worms.io',
        gameId: 'angry-worms-io',
        date: '2026-05-13',
        readTime: '11 min',
        excerpt: 'Learn how to grow your worm, trap opponents, use boost effectively, and dominate the leaderboard.',
        difficulty: 'Beginner'
    },
    {
        id: 'smashkarts-io-guide',
        title: 'SmashKarts.io Guide: Master Kart Combat',
        game: 'SmashKarts.io',
        gameId: 'smashkarts-io',
        date: '2026-05-12',
        readTime: '11 min',
        excerpt: 'Learn weapon strategies, map control, driving tips, and pro tactics to dominate the leaderboard.',
        difficulty: 'Intermediate'
    },
    {
        id: 'surviv-io-guide',
        title: 'Surviv.io Complete Guide: Master 2D Battle Royale',
        game: 'Surviv.io',
        gameId: 'surviv-io',
        date: '2024-01-15',
        readTime: '14 min',
        excerpt: 'Learn weapons, map strategies, and survival tactics to become the last survivor.',
        difficulty: 'Intermediate'
    },
    {
        id: 'bloxd-io-guide',
        title: 'Bloxd.io Complete Guide: Bedwars, Parkour & PvP',
        game: 'Bloxd.io',
        gameId: 'bloxd-io',
        date: '2026-05-25',
        readTime: '13 min',
        excerpt: 'Master all game modes including Bedwars strategies, building mechanics, and PvP combat.',
        difficulty: 'Intermediate'
    },
    {
        id: 'crazysteve-io-guide',
        title: 'CrazySteve.io Guide: Block-Building Battle Royale',
        game: 'CrazySteve.io',
        gameId: 'crazysteve-io',
        date: '2026-05-16',
        readTime: '10 min',
        excerpt: 'Master block-building combat strategies and battle royale survival tactics in CrazySteve.io.',
        difficulty: 'Beginner'
    },
    {
        id: 'curser-io-guide',
        title: 'Curser.io Guide: Navigate & Survive the Cursor Wars',
        game: 'Curser.io',
        gameId: 'curser-io',
        date: '2026-05-17',
        readTime: '7 min',
        excerpt: 'Master cursor movement, survival tactics, and browser battlefield navigation in Curser.io.',
        difficulty: 'Beginner'
    },
    {
        id: 'blumgi-rocket-guide',
        title: 'Blumgi Rocket Guide: Launch, Fly & Land Perfectly',
        game: 'Blumgi Rocket',
        gameId: 'blumgi-rocket',
        date: '2026-05-19',
        readTime: '9 min',
        excerpt: 'Master rocket launch mechanics, trajectory prediction, and precision landing in Blumgi Rocket.',
        difficulty: 'Intermediate'
    },
    {
        id: 'shell-shockers-guide',
        title: 'Shell Shockers Complete Guide: Best Classes & Weapons',
        game: 'Shell Shockers',
        gameId: 'shell-shockers',
        date: '2024-01-15',
        readTime: '12 min',
        excerpt: 'Learn class selection, weapon comparisons, and map strategies for egg combat.',
        difficulty: 'Intermediate'
    },
    {
        id: 'mope-io-guide',
        title: 'Mope.io Complete Guide: Animal Evolution & Survival',
        game: 'Mope.io',
        gameId: 'mope-io',
        date: '2024-01-15',
        readTime: '13 min',
        excerpt: 'Master animal evolution routes, food chain strategies, and survival tips.',
        difficulty: 'Beginner'
    },
    {
        id: 'venge-io-guide',
        title: 'Venge.io Complete Guide: Best Classes & Combat',
        game: 'Venge.io',
        gameId: 'venge-io',
        date: '2024-01-15',
        readTime: '11 min',
        excerpt: 'Learn FPS combat tactics, class selection, and weapon loadouts.',
        difficulty: 'Advanced'
    },
    {
        id: 'gartic-io-guide',
        title: 'Gartic.io Complete Guide: Drawing & Guessing Tips',
        game: 'Gartic.io',
        gameId: 'gartic-io',
        date: '2024-01-15',
        readTime: '11 min',
        excerpt: 'Master drawing techniques, guessing strategies, and room settings.',
        difficulty: 'Beginner'
    },
    {
        id: 'wings-io-guide',
        title: 'Wings.io Complete Guide: Master Dogfighting',
        game: 'Wings.io',
        gameId: 'wings-io',
        date: '2024-01-15',
        readTime: '10 min',
        excerpt: 'Learn plane combat, aircraft selection, and aerial combat tactics.',
        difficulty: 'Intermediate'
    },
    {
        id: 'moomoo-io-guide',
        title: 'MooMoo.io Complete Guide: Base Building & Survival',
        game: 'MooMoo.io',
        gameId: 'moomoo-io',
        date: '2024-01-15',
        readTime: '12 min',
        excerpt: 'Master base designs, resource management, and PvP defense strategies.',
        difficulty: 'Intermediate'
    },
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
    },
    {
        id: 'defend-io-guide',
        title: 'Defend.io Guide: Tower Defense Strategy & Tips',
        game: 'Defend.io',
        gameId: 'defend-io',
        date: '2026-05-22',
        readTime: '8 min',
        excerpt: 'Master tower placement, upgrade strategies, and wave defense tactics in Defend.io.',
        difficulty: 'Beginner'
    },
    {
        id: 'hole-io-guide',
        title: 'Hole.io Guide: Grow, Swallow & Dominate the City',
        game: 'Hole.io',
        gameId: 'hole-io',
        date: '2026-05-21',
        readTime: '8 min',
        excerpt: 'Master city swallowing, vehicle chasing, map control, and absorbing smaller holes in Hole.io.',
        difficulty: 'Beginner'
    },
    {
        id: 'paper-io-guide',
        title: 'Paper.io Guide: Claim Territory & Defend Your Zone',
        game: 'Paper.io',
        gameId: 'paper-io',
        date: '2026-05-20',
        readTime: '8 min',
        excerpt: 'Master territory claiming, zone defense, and trail-cutting strategies in Paper.io.',
        difficulty: 'Beginner'
    },
    {
        id: 'dogod-io-guide',
        title: 'Dogod.io Guide: Evolve & Dominate the Food Chain',
        game: 'Dogod.io',
        gameId: 'dogod-io',
        date: '2026-05-23',
        readTime: '9 min',
        excerpt: 'Master evolution mechanics, food chain strategies, and predator-prey tactics to become the apex predator.',
        difficulty: 'Beginner'
    },
    {
        id: 'angry-worms-io-guide',
        title: 'Angry Worms.io Guide: Master the Slither-Style Arena',
        game: 'Angry Worms.io',
        gameId: 'angry-worms-io',
        date: '2026-05-24',
        readTime: '11 min',
        excerpt: 'Proven strategies to grow your worm and dominate the Angry Worms.io arena. From basic controls to advanced traps.',
        difficulty: 'Beginner'
    },
    {
        id: 'repuls-io-guide',
        title: 'Repuls.io Guide: FPS Combat & Map Control',
        game: 'Repuls.io',
        gameId: 'repuls-io',
        date: '2026-05-26',
        readTime: '10 min',
        excerpt: 'Master the unique repulsion launcher mechanics, weapon loadouts, and tactical movement in this fast-paced FPS arena shooter.',
        difficulty: 'Intermediate'
    },
    {
        id: 'spawner-io-guide',
        title: 'Spawner.io Guide: Build Defenses & Survive',
        game: 'Spawner.io',
        gameId: 'spawner-io',
        date: '2026-05-28',
        readTime: '8 min',
        excerpt: 'Master block spawning, defense building, and survival tactics in this unique tower defense .io game.',
        difficulty: 'Beginner'
    },
    {
        id: 'gulper-io-guide',
        title: 'Gulper.io Guide: Grow Big & Dominate the Arena',
        game: 'Gulper.io',
        gameId: 'gulper-io',
        date: '2026-05-29',
        readTime: '10 min',
        excerpt: 'Master the gulper mechanics, grow your creature, eat opponents, and climb the leaderboard with proven strategies.',
        difficulty: 'Intermediate'
    },
    {
        id: 'starblast-io-guide',
        title: 'Starblast.io Guide: Mine, Upgrade & Survive in Space',
        game: 'Starblast.io',
        gameId: 'starblast-io',
        date: '2026-05-30',
        readTime: '11 min',
        excerpt: 'Master spaceship upgrades, mining strategies, combat tactics, and survival tips in deep space battles.',
        difficulty: 'Intermediate'
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
    const game = gamesData.find(g => g.id === guide.gameId);
    const icon = game ? game.icon : '🎮';
    const iconColor = game ? game.iconColor : '#666';
    return `
        <a href="guides/${guide.id}.html" class="guide-card">
            <div class="guide-thumb" style="background: ${iconColor}20; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 2.5rem;">${icon}</span>
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
