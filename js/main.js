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
                window.location.href = `games?search=${encodeURIComponent(query)}`;
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
    id: 'krunker-io',
    name: 'Krunker.io',
    icon: '🎯',
    iconColor: '#ff6b35',
    guideCount: 5,
    difficulty: 4,
    tags: ['FPS', 'Shooter', 'Combat'],
    description: 'Fast-paced first-person shooter .io game.'
    },
    {
    id: 'deeeep-io',
    name: 'Deeeep.io',
    icon: '🐟',
    iconColor: '#0077b6',
    guideCount: 1,
    difficulty: 3,
    tags: ['Evolution', 'Survival', 'Ocean'],
    description: 'Underwater evolution game with 100+ sea creatures.'
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
        id: 'hexanaut-io',
        name: 'Hexanaut.io',
        icon: '⬡',
        iconColor: '#00d4ff',
        guideCount: 1,
        difficulty: 3,
        tags: ['Territory', 'Strategy', 'Hexagon'],
        description: '3D territory conquest game with hexagonal grid mechanics. Capture hexagons, grab totems, and become the King.'
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
    id: 'sandboxels',
    name: 'Sandboxels',
    icon: '🧪',
    iconColor: '#ffeb3b',
    guideCount: 6,
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
    id: 'stickman-hook',
    name: 'Stickman Hook',
    icon: '🪝',
    iconColor: '#ff5722',
    guideCount: 1,
    difficulty: 2,
    tags: ['Physics', 'Swing', 'Arcade'],
    description: 'Physics-based grappling hook swing game.'
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
    },
    {
    id: 'spinner-io',
    name: 'Spinner.io',
    icon: '🌀',
    iconColor: '#06b6d4',
    guideCount: 1,
    difficulty: 2,
    tags: ['Battle', 'Spinning', 'Arena'],
    description: 'Master spinning combat tactics, grow your spinner by defeating opponents, and dominate the arena.'
    },
    {
    id: 'snowball-io',
    name: 'Snowball.io',
    icon: '❄️',
    iconColor: '#38bdf8',
    guideCount: 1,
    difficulty: 2,
    tags: ['Winter', 'Battle', 'Physics'],
    description: 'Roll snowballs, knock opponents off ice platforms, and dominate winter battles.'
    },
    {
    id: 'goons-io',
    name: 'Goons.io',
    icon: '⚔️',
    iconColor: '#10b981',
    guideCount: 1,
    difficulty: 2,
    tags: ['Sword Combat', 'Medieval', 'Battle'],
    description: 'Master sword combat, block and dodge attacks, and survive medieval arena battles in Goons.io.'
    },
    {
    id: 'littlebigsnake-io',
    name: 'LittleBigSnake.io',
    icon: '🐍',
    iconColor: '#10b981',
    guideCount: 1,
    difficulty: 2,
    tags: ['Snake', 'Evolution', 'Flying'],
    description: 'Grow your snake, evolve into a flying dragonfly, and dominate the food chain in LittleBigSnake.io.'
    },
    {
    id: 'lordz-io',
    name: 'Lordz.io',
    icon: '⚔️',
    iconColor: '#e94560',
    guideCount: 1,
    difficulty: 5,
    tags: ['Strategy', 'RTS', 'Medieval'],
    description: 'Real-time strategy game where you build armies, manage resources, and conquer territories in medieval warfare.'
    },
    {
    id: 'hordes-io',
    name: 'Hordes.io',
    icon: '⚔️',
    iconColor: '#8b5cf6',
    guideCount: 1,
    difficulty: 4,
    tags: ['MMORPG', 'PvP', 'Fantasy'],
    description: '3D browser MMORPG with 4 unique classes. Master Warriors, Archers, Mages, and Shamans in epic PvP battles.'
    },
    {
    id: 'liquid-swarm',
    name: 'Liquid Swarm',
    icon: '🌀',
    iconColor: '#4fc3f7',
    guideCount: 1,
    difficulty: 2,
    tags: ['Arcade', 'Roguelite', 'Growth'],
    description: 'Fast-paced arcade roguelite where you surround and absorb enemy swarms to grow your own.'
    },
    {
    id: 'splix-io',
    name: 'Splix.io',
    icon: '🟩',
    iconColor: '#4caf50',
    guideCount: 1,
    difficulty: 3,
    tags: ['Strategy', 'Territory', 'Grid'],
    description: 'Territory capture game where you expand your colored blocks on a shared grid while protecting your vulnerable trail.'
    },
    {
    id: 'superhex-io',
    name: 'Superhex.io',
    icon: '⬡',
    iconColor: '#7c4dff',
    guideCount: 1,
    difficulty: 3,
    tags: ['Territory', 'Strategy', 'Hex'],
    description: 'Claim hexagonal territory and defend your zone in this strategic grid-based .io game.'
    },
    {
    id: 'voxelim-io',
    name: 'Voxelim.io',
    icon: '🧱',
    iconColor: '#795548',
    guideCount: 1,
    difficulty: 3,
    tags: ['Building', 'Combat', 'Voxel'],
    description: 'Build structures and battle enemies in a voxel-based multiplayer world.'
    },
    {
    id: 'warden-io',
    name: 'Warden.io',
    icon: '🗡️',
    iconColor: '#607d8b',
    guideCount: 1,
    difficulty: 4,
    tags: ['RPG', 'Dungeon', 'Boss'],
    description: 'Dungeon crawler with class builds, boss fights, and strategic combat in a mystical arena.'
    },
    {
    id: 'wormate-io',
    name: 'Wormate.io',
    icon: '🐛',
    iconColor: '#ff9800',
    guideCount: 1,
    difficulty: 2,
    tags: ['Snake', 'Growth', 'Arena'],
    description: 'Collect sweet treats, grow your worm, and dominate the arena with upgrade strategies.'
    },
    {
    id: 'wormax-io',
    name: 'Wormax.io',
    icon: '🪱',
    iconColor: '#8bc34a',
    guideCount: 1,
    difficulty: 2,
    tags: ['Snake', 'Growth', 'Classic'],
    description: 'Slither smart, use boost strategically, and grow into the biggest worm on the server.'
    },
    {
    id: 'zapper-io',
    name: 'Zapper.io',
    icon: '⚡',
    iconColor: '#ffc107',
    guideCount: 1,
    difficulty: 3,
    tags: ['Combat', 'Arena', 'Fast'],
    description: 'Lightning-fast arena combat with weapon upgrades and movement-based tactics.'
    },
    {
    id: 'poxel-io',
    name: 'Poxel.io',
    icon: '🔫',
    iconColor: '#ff6b35',
    guideCount: 1,
    difficulty: 4,
    tags: ['FPS', 'Multiplayer', 'Pixel'],
    description: 'Fast-paced pixel FPS with 30+ maps, 20+ weapons, and 4 competitive game modes. Master weapons, learn maps, and dominate the leaderboard.'
    },
    {
    id: 'war-brokers',
    name: 'War Brokers',
    icon: '🎖️',
    iconColor: '#4a5568',
    guideCount: 1,
    difficulty: 4,
    tags: ['FPS', 'Vehicles', 'Battle Royale'],
    description: 'Military FPS with tanks, helicopters, and 17 weapons. Master combined-arms combat across multiple game modes.'
    },
    {
    id: 'starve-io',
    name: 'Starve.io',
    icon: '⚒️',
    iconColor: '#4caf50',
    guideCount: 1,
    difficulty: 4,
    tags: ['Survival', 'Crafting', 'PvP'],
    description: 'Multiplayer sandbox survival game with deep crafting, biomes, and combat.'
    },
    {
    id: '1v1-lol',
    name: '1v1.LOL',
    icon: '🎯',
    iconColor: '#ff5722',
    guideCount: 1,
    difficulty: 3,
    tags: ['Shooter', 'Building', 'FPS'],
    description: 'Fortnite-style browser shooter with real-time building mechanics.'
    },
    {
    id: 'deadshot-io',
    name: 'DeadShot.io',
    icon: '🔫',
    iconColor: '#2196f3',
    guideCount: 1,
    difficulty: 4,
    tags: ['FPS', 'Shooter', 'Arena'],
    description: 'Fast-paced browser FPS with slide-jump movement. Master weapons, aim for headshots, dominate every map.'
    }
,
{
    id: 'curve-fever-pro',
    name: 'Curve Fever Pro',
    icon: '🌀',
    iconColor: '#ff6b35',
    guideCount: 1,
    difficulty: 4,
    tags: ['Arcade', 'Multiplayer', 'Powers'],
    description: 'Fast-paced multiplayer browser game with 30 unique powers. Control a ship, leave deadly trails, and dominate the arena.'
    },
    {
    id: 'kirka-io',
    name: 'Kirka.io',
    icon: '🧱',
    iconColor: '#4caf50',
    guideCount: 1,
    difficulty: 3,
    tags: ['FPS', 'Pixel', 'Arena'],
    description: 'Voxel FPS browser game. Master wall climbing, dashing, and pixel-perfect combat.'
    },
    {
    id: 'kour-io',
    name: 'Kour.io',
    icon: '🏃',
    iconColor: '#ff9800',
    guideCount: 1,
    difficulty: 4,
    tags: ['FPS', 'Parkour', 'Class-based'],
    description: 'Class-based FPS with parkour movement. Master 13 unique classes and dominate every match.'
    },
    {name:"Ninja.io",id:"ninja-io",slug:"ninja-io",icon:"🥷",iconColor:"#4A0E4E",guideCount:1,difficulty:5,tags:["动作","多人","射击"]},
    {name:"Arrow Arena",id:"arrow-arena",slug:"arrow-arena",icon:"🏹",iconColor:"#FF6B35",guideCount:1,difficulty:2,tags:["Archery","IO","Pixel"],description:"Pixel archery combat with skill upgrades and leaderboard ranking."},
    {name:"Bonk.io",id:"bonk-io",slug:"bonk-io",icon:"⚽",iconColor:"#2196F3",guideCount:1,difficulty:3,tags:["Physics","Multiplayer","Classic"],description:"Physics-based multiplayer ball combat game."},
    {name:"Ev.io",id:"ev-io",slug:"ev-io",icon:"🔫",iconColor:"#00BCD4",guideCount:1,difficulty:3,tags:["FPS","Cyberpunk","Blockchain"],description:"Cyberpunk browser FPS with play-to-earn mechanics. Choose weapons, customize abilities, and dominate the arena."},
    {name:"SchoolBreak.io",id:"schoolbreak-io",slug:"schoolbreak-io",icon:"🎒",iconColor:"#FF9800",guideCount:1,difficulty:2,tags:["Asymmetric","Party","Multiplayer"],description:"Student vs Teacher chaos! Cause mayhem or enforce discipline in this unique asymmetric multiplayer game."},
    {name:"Florr.io",id:"florr-io",slug:"florr-io",icon:"🌸",iconColor:"#E91E63",guideCount:1,difficulty:4,tags:["Flower","Crafting","PvP","Farming"],description:"Unique multiplayer .io game where you play as a flower with orbiting petals. Collect, craft, and battle through diverse biomes."},
    {
        id: 'tetr-io',
        name: 'TETR.IO',
        icon: '🧩',
        iconColor: '#6366f1',
        guideCount: 1,
        difficulty: 3,
        tags: ['Puzzle', 'Competitive', 'Multiplayer'],
        description: 'Competitive online Tetris with ranked play, T-spins, and advanced mechanics.',
        url: 'https://tetr.io',
        image: 'tetr-io'
    }
,
    {
        id: 'devast-io',
        name: 'Devast.io',
        icon: '☢️',
        iconColor: '#4CAF50',
        guideCount: 1,
        difficulty: 4,
        tags: ['Survival', 'Crafting', 'Base Building', 'PvP'],
        description: 'Post-apocalyptic survival io game with resource gathering, base building, crafting, and radioactive wasteland combat.'
    }
];

/* ========================================
   攻略数据（用于动态渲染）
   ======================================== */
const guidesData = [
{
    id: 'tetr-io-guide',
    title: 'TETR.IO Guide: Master Competitive Online Tetris & Ranked Play',
    game: 'TETR.IO',
    gameId: 'tetr-io',
    date: '2026-06-23',
    url: 'tetr-io-guide',
    image: 'tetr-io',
    description: 'Complete guide to TETR.IO: T-spins, combos, B2B chains, Tetra League ranked strategies, and all game modes explained.'
},
    {
    id: 'curve-fever-pro-guide',
    title: 'Curve Fever Pro Guide: Master Trail Combat & Powers',
    game: 'Curve Fever Pro',
    gameId: 'curve-fever-pro',
    date: '2026-06-19',
    readTime: '13 min',
    excerpt: 'Master Curve Fever Pro with our complete guide. Learn trail combat tactics, power strategies, and arena domination tips.',
    image: '/images/games/curve-fever-pro/hero.jpg',
    url: '/guides/curve-fever-pro-guide',
    difficulty: 'Advanced',
    category: 'Arcade',
    tags: ['arcade', 'multiplayer', 'powers', 'trail', 'strategy']
    },
    {
        id: 'deadshot-io-guide',
        title: 'DeadShot.io Guide: Master Movement, Weapons & Dominate Every Match',
        game: 'DeadShot.io',
        gameId: 'deadshot-io',
        date: '2026-06-18',
        readTime: '9 min',
        excerpt: 'Master DeadShot.io with our complete guide. Learn slide jumping, weapon stats, map strategies, and pro tips to climb the leaderboard.',
        image: '/images/games/deadshot-io/hero.jpg',
        url: '/guides/deadshot-io-guide',
        difficulty: 'Advanced',
        category: 'FPS',
        tags: ['fps', 'shooter', 'browser', 'deadshot', 'movement']
    },
        {
        id: 'hexanaut-io-guide',
        title: 'Hexanaut.io Guide: Master Territory Capture & King Strategy',
        game: 'Hexanaut.io',
        gameId: 'hexanaut-io',
        date: '2026-06-18',
        readTime: '10 min',
        excerpt: 'Conquer the hexagonal battlefield in Hexanaut.io. Master territory capture, totem strategies, and King victory tactics.',
        image: '/images/games/hexanaut-io/hero.jpg',
        url: '/guides/hexanaut-io-guide',
        difficulty: 'Intermediate',
        category: 'Territory Strategy',
        tags: ['territory', 'strategy', 'multiplayer', 'hexagon', '3D']
    },
{
        id: '1v1-lol-guide',
        title: '1v1.LOL Guide: Master Building & Shooting in Fortnite-Style Browser Game',
        game: '1v1.LOL',
        gameId: '1v1-lol',
        date: '2026-06-17',
        readTime: '12 min',
        excerpt: 'Master building and shooting in 1v1.LOL. Learn 90-degree turns, box fighting, weapon combos, and advanced tactics.',
        image: '/images/games/1v1-lol/hero.jpg',
        url: '/guides/1v1-lol-guide',
        difficulty: 'Intermediate',
        tags: ['shooter', 'building', 'fps', 'fortnite']
    },
    {
        id: 'splix-io-guide',
        title: 'Splix.io Guide: Master Territory Capture & Dominate the Grid',
        game: 'Splix.io',
        gameId: 'splix-io',
        date: '2026-06-13',
        readTime: '10 min',
        excerpt: 'Master Splix.io territory capture strategies, trail protection tactics, and leaderboard climbing tips to dominate the grid.',
        difficulty: 'Intermediate'
    },
    {
        id: 'superhex-io-guide',
        title: 'Superhex.io Guide: Claim Territory & Defend Your Hex',
        game: 'Superhex.io',
        gameId: 'superhex-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Superhex.io territory control strategies, hex claiming mechanics, and defense tactics to dominate the map.',
        difficulty: 'Intermediate'
    },
    {
        id: 'voxelim-io-guide',
        title: 'Voxelim.io Guide: Build & Battle in a Voxel World',
        game: 'Voxelim.io',
        gameId: 'voxelim-io',
        date: '2026-06-13',
        readTime: '9 min',
        excerpt: 'Master Voxelim.io voxel building mechanics, combat strategies, and resource gathering for battlefield domination.',
        difficulty: 'Intermediate'
    },
    {
        id: 'warden-io-guide',
        title: 'Warden.io Guide: Dungeon Crawler Strategy & Boss Tips',
        game: 'Warden.io',
        gameId: 'warden-io',
        date: '2026-06-13',
        readTime: '9 min',
        excerpt: 'Master Warden.io dungeon crawling strategies, boss fight tactics, and class builds for the mystical arena.',
        difficulty: 'Intermediate'
    },
    {
        id: 'wormate-io-guide',
        title: 'Wormate.io Guide: Sweet Treats & Giant Worms',
        game: 'Wormate.io',
        gameId: 'wormate-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Wormate.io sweet food collection, worm upgrades, and arena tactics for growth and survival.',
        difficulty: 'Beginner'
    },
    {
        id: 'wormax-io-guide',
        title: 'Wormax.io Guide: Slither Smart & Grow Massive',
        game: 'Wormax.io',
        gameId: 'wormax-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Wormax.io smart slithering, boost mastery, and strategies to become the biggest worm on the server.',
        difficulty: 'Beginner'
    },
    {
        id: 'zapper-io-guide',
        title: 'Zapper.io Guide: Lightning-Fast Combat Tips',
        game: 'Zapper.io',
        gameId: 'zapper-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Zapper.io lightning combat tactics, movement strategies, and weapon upgrades to dominate the arena.',
        difficulty: 'Intermediate'
    },
    {
        id: 'bonk-io-guide',
        title: 'Bonk.io Guide: Master Physics Combat & Knockouts',
        game: 'Bonk.io',
        gameId: 'bonk-io',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master Bonk.io with our complete guide. Learn physics mechanics, heavy mode timing, map strategies, and pro tips to knock every opponent off.',
        difficulty: 'Intermediate'
    },
    {
        id: 'nobrakes-io-guide',
        title: 'NoBrakes.io Guide: Drift, Boost & Race to First',
        game: 'NoBrakes.io',
        gameId: 'nobrakes-io',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master NoBrakes.io with our complete guide. Learn drift mechanics, boost timing, track shortcuts, and racing strategies to leave your opponents in the dust.',
        difficulty: 'Beginner'
    },
    {
        id: 'liquid-swarm-guide',
        title: 'Liquid Swarm Guide: Master the Ultimate Consuming Force',
        game: 'Liquid Swarm',
        gameId: 'liquid-swarm',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master Liquid Swarm with this complete guide. Learn the surround mechanic, power-up strategies, and pro tips to become the ultimate consuming force.',
        difficulty: 'Beginner'
    },
    {
        id: 'venge-io-guide',
        title: 'Venge.io Guide: Master FPS Arena Combat',
        game: 'Venge.io',
        gameId: 'venge-io',
        date: '2026-06-11',
        readTime: '10 min',
        excerpt: 'Master Venge.io with this complete guide. Covers controls, hero abilities, game modes, and top strategies to dominate the arena.',
        difficulty: 'Beginner'
    },
    {
        id: 'zombsroyale-io-guide',
        title: 'ZombsRoyale.io Complete Guide: Battle Royale Tactics',
        game: 'ZombsRoyale.io',
        gameId: 'zombsroyale-io',
        date: '2026-06-11',
        readTime: '10 min',
        excerpt: 'Master battle royale tactics in ZombsRoyale.io. Learn landing strategies, weapon selection, combat tips, and circle control to become the last survivor.',
        difficulty: 'Beginner'
    },
    {
        id: 'evowars-io-guide',
        title: 'EvoWars.io Complete Guide 2024: Master Evolution \u0026 Combat',
        game: 'EvoWars.io',
        gameId: 'evowars-io',
        date: '2026-06-09',
        readTime: '9 min',
        excerpt: 'Master evolution mechanics, food chain strategies, and predator-prey tactics to become the apex predator.',
        difficulty: 'Beginner'
    },
    {
        id: 'lordz-io-guide',
        title: 'Lordz.io Guide: Build Your Medieval Empire and Conquer the Battlefield',
        game: 'Lordz.io',
        gameId: 'lordz-io',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master Lordz.io with our complete guide. Learn unit stats, economy strategy, army composition, and pro tips to dominate the medieval battlefield.',
        difficulty: 'Intermediate',
        badge: '🏰'
    },
    {
        id: 'hordes-io-guide',
        title: 'Hordes.io Guide: Master 4 Classes & PvP Combat',
        game: 'Hordes.io',
        gameId: 'hordes-io',
        date: '2026-06-13',
        readTime: '10 min',
        excerpt: 'Master Hordes.io with our complete guide. Learn Warrior, Archer, Mage, and Shaman skills, PvP combos, and pro strategies.',
        difficulty: 'Intermediate',
        badge: '⚔️'
    },
    {
        id: 'skribbl-io-guide',
        title: 'Skribbl.io Complete Guide: Master Drawing \u0026 Guessing Tips',
        game: 'Skribbl.io',
        gameId: 'skribbl-io',
        date: '2026-06-08',
        readTime: '10 min',
        excerpt: 'Master the art of drawing and guessing! Learn pro drawing techniques, guessing strategies, custom room settings, and become the ultimate Skribbl champion.',
        difficulty: 'Beginner'
    },
    {
        id: 'taming-io-guide',
        title: 'Taming.io Guide: Master Pet Taming & Base Building',
        game: 'Taming.io',
        gameId: 'taming-io',
        date: '2026-06-07',
        readTime: '10 min',
        excerpt: 'Build your ultimate pet army! Learn pet taming mechanics, base defense, elemental combat, and climb the leaderboard.',
        difficulty: 'Beginner'
    },
    {
        id: 'stickman-hook-guide',
        title: 'Stickman Hook Guide: Master the Swing & Conquer Every Level',
        game: 'Stickman Hook',
        gameId: 'stickman-hook',
        date: '2026-06-16',
        readTime: '8 min',
        excerpt: 'Master swinging mechanics, release timing, level strategies, and pro tips to dominate every stage in Stickman Hook.',
        difficulty: 'Beginner'
    },
    {
        id: 'krunker-io-guide',
        title: 'Krunker.io Guide: Master FPS Combat & Movement',
        game: 'Krunker.io',
        gameId: 'krunker-io',
        date: '2026-06-05',
        readTime: '12 min',
        excerpt: 'Master FPS combat tactics, movement strategies, class selection, weapon tips, and dominate the battlefield in Krunker.io.',
        difficulty: 'Intermediate'
    },
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
        id: 'spinner-io-guide',
        title: 'Spinner.io Guide: Spin to Win in the Arena',
        game: 'Spinner.io',
        gameId: 'spinner-io',
        date: '2026-05-30',
        readTime: '9 min',
        excerpt: 'Master spinning combat tactics, grow your spinner by defeating opponents, and dominate the arena with proven strategies.',
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
    },
    {
        id: 'yohoho-io-guide',
        title: 'Yohoho.io Guide: Master Pirate Battle Royale',
        game: 'Yohoho.io',
        gameId: 'yohoho-io',
        date: '2026-05-31',
        readTime: '10 min',
        excerpt: 'Master pirate combat, collect coins, upgrade your ship, and become the ultimate pirate in Yohoho.io battle royale.',
        difficulty: 'Beginner'
    },
    {
        id: 'snowball-io-guide',
        title: 'Snowball.io Guide: Roll, Throw & Knock Out',
        game: 'Snowball.io',
        gameId: 'snowball-io',
        date: '2026-05-31',
        readTime: '9 min',
        excerpt: 'Master snowball mechanics, push opponents off platforms, and dominate winter battles with proven strategies.',
        difficulty: 'Beginner'
    },
    {
        id: 'goons-io-guide',
        title: 'Goons.io Guide: Sword Combat & Survival Tips',
        game: 'Goons.io',
        gameId: 'goons-io',
        date: '2026-06-03',
        readTime: '9 min',
        excerpt: 'Master sword combat tactics, block and dodge attacks, and survive medieval arena battles with proven strategies.',
        difficulty: 'Beginner'
    },
    {
        id: 'littlebigsnake-io-guide',
        title: 'LittleBigSnake.io Guide: Fly, Grow & Dominate',
        game: 'LittleBigSnake.io',
        gameId: 'littlebigsnake-io',
        date: '2026-06-04',
        readTime: '9 min',
        excerpt: 'Master snake growth mechanics, evolve into flying dragonfly form, and dominate the food chain with proven strategies.',
        difficulty: 'Beginner'
    },
    {
        id: 'sandboxels-guide',
        title: 'Sandboxels Guide: Master Physics Simulations',
        game: 'Sandboxels',
        gameId: 'sandboxels',
        date: '2026-06-06',
        readTime: '8 min',
        excerpt: 'Master element interactions, create amazing physics simulations, and explore 500+ elements in this creative sandbox game.',
        difficulty: 'Beginner'
    },
    {
        id: 'poxel-io-guide',
        title: 'Poxel.io Guide: Master Weapons, Game Modes & Pixel FPS Tactics',
        game: 'Poxel.io',
        gameId: 'poxel-io',
        date: '2026-06-14',
        readTime: '10 min',
        excerpt: 'Master Poxel.io with our complete guide. Learn all 4 game modes, best weapon loadouts, map strategies, and pro tips to dominate the pixel FPS battlefield.',
        difficulty: 'Intermediate',
        badge: '🔫'
    },
    {
        id: 'war-brokers-guide',
        title: 'War Brokers Guide: Master Vehicles, Weapons & Game Modes',
        game: 'War Brokers',
        gameId: 'war-brokers',
        date: '2026-06-16',
        readTime: '12 min',
        excerpt: 'Master War Brokers.io with our complete guide. Learn all 17 weapons, vehicle combat tactics, game modes, and battle royale strategies to dominate the battlefield.',
        difficulty: 'Advanced',
        badge: '🎖️'
    },
    {
        id: 'starve-io-guide',
        title: 'Starve.io Guide: Survival, Crafting & Biome Mastery',
        game: 'Starve.io',
        gameId: 'starve-io',
        date: '2026-06-17',
        readTime: '15 min',
        excerpt: 'Master Starve.io with our complete survival guide. Learn crafting recipes, biome strategies, combat tips, and base building to survive and thrive.',
        difficulty: 'Advanced',
        badge: '⚒️'
    },
    {
        id: 'deeeep-io-guide',
        title: 'Deeeep.io Guide: Master Ocean Evolution & Survival',
        game: 'Deeeep.io',
        gameId: 'deeeep-io',
        date: '2026-06-20',
        readTime: '14 min',
        excerpt: 'Master Deeeep.io with evolution paths, creature abilities, biome strategies, and survival tactics to become the apex predator.',
        difficulty: 'Intermediate',
        badge: '🐟'
    },
    {
        id: 'kirka-io-guide',
        title: 'Kirka.io Guide: Master Voxel FPS Combat & Weapons',
        game: 'Kirka.io',
        gameId: 'kirka-io',
        date: '2026-06-20',
        readTime: '9 min',
        excerpt: 'Master Kirka.io with our complete guide. Learn weapon stats, game modes, wall climbing, and pro tips to dominate the voxel arena.',
        difficulty: 'Intermediate',
        badge: '🧱'
    },
    {
        id: 'kour-io-guide',
        title: 'Kour.io Guide: Master 13 Classes, Parkour & Gun Game',
        game: 'Kour.io',
        gameId: 'kour-io',
        date: '2026-06-20',
        readTime: '9 min',
        excerpt: 'Master Kour.io with our complete guide. Learn all 13 classes, parkour movement, game modes, and pro tips to dominate every match.',
        difficulty: 'Advanced',
        badge: '🏃'
    },
    {slug:"ninja-io-guide",name:"Ninja.io",title:"Ninja.io Guide: Master Weapons, Movement & Game Modes",date:"2026-06-21",difficulty:"Advanced",readTime:11,url:"https://iogameguide.com/guides/ninja-io-guide",image:"https://iogameguide.com/images/games/ninja-io/hero.jpg"},
    {slug:"arrow-arena-guide",name:"Arrow Arena",title:"Arrow Arena Guide: Master Archery Combat",date:"2026-06-21",difficulty:2,readTime:8,url:"https://iogameguide.com/guides/arrow-arena-guide",image:"https://iogameguide.com/images/games/arrow-arena/hero.jpg"},
    {slug:"bonk-io-guide",name:"Bonk.io",title:"Bonk.io Guide: Master Physics Combat",date:"2026-06-21",difficulty:3,readTime:8,url:"https://iogameguide.com/guides/bonk-io-guide",image:"https://iogameguide.com/images/games/bonk-io/hero.jpg"},
    {slug:"ev-io-guide",name:"Ev.io",title:"Ev.io Guide: Master Weapons, Abilities & Arena Combat",date:"2026-06-22",difficulty:3,readTime:8,url:"https://iogameguide.com/guides/ev-io-guide",image:"https://iogameguide.com/images/games/ev-io/hero.jpg"},
    {slug:"schoolbreak-io-guide",name:"SchoolBreak.io",title:"SchoolBreak.io Guide: Master Chaos & Discipline",date:"2026-06-22",difficulty:2,readTime:8,url:"https://iogameguide.com/guides/schoolbreak-io-guide",image:"https://iogameguide.com/images/games/schoolbreak-io/hero.jpg"},
    {slug:"florr-io-guide",name:"Florr.io",title:"Florr.io Guide: Master Petals, Crafting & Biome Combat",date:"2026-06-22",difficulty:4,readTime:12,url:"https://iogameguide.com/guides/florr-io-guide",image:"https://iogameguide.com/images/games/florr-io/hero.jpg"},
,
    {
        slug: 'devast-io-guide',
        name: 'Devast.io',
        title: 'Devast.io Guide: Master Survival, Crafting & Base Building',
        date: '2026-06-24',
        difficulty: 4,
        readTime: 12,
        url: 'https://iogameguide.com/guides/devast-io-guide',
        image: 'https://iogameguide.com/images/games/devast-io/hero.jpg'
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
        <a href="guides/${game.id}-guide" class="game-card">
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
        <a href="guides/${guide.id}" class="guide-card">
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

