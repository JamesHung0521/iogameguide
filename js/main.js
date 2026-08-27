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
/* ========================================
   游戏数据 - 标准格式模板
   新增游戏必须严格按此格式，9个字段缺一不可
   
   {
       id: 'xxx',                 // 游戏ID（slug格式，如 tetr-io）
       name: 'Game Name',         // 游戏名
       icon: '🎮',                // emoji图标
       iconColor: '#xxxxxx',      // 品牌色（hex）
       guideCount: 1,             // 攻略数量
       difficulty: 3,             // 数字 1-5
       tags: ['tag1', 'tag2'],    // 标签数组
       description: '...',        // 英文描述（必填！缺失会导致页面崩溃）
   }
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
    },

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
    {name:"NoBrakes.io",id:"nobrakes-io",slug:"nobrakes-io",icon:"🏎️",iconColor:"#E63946",guideCount:1,difficulty:2,tags:["竞速","漂移","多人"],description:"Drift-based multiplayer racing game with boost mechanics and track shortcuts."},
    {gameId:"ninja-io",name:"Ninja.io",id:"ninja-io",slug:"ninja-io",icon:"🥷",iconColor:"#4A0E4E",guideCount:1,difficulty:5,tags:["动作","多人","射击"],description:"Fast-paced multiplayer shooting game with ninja-themed combat, weapons, and agile movement."},
    {gameId:"arrow-arena",name:"Arrow Arena",id:"arrow-arena",slug:"arrow-arena",icon:"🏹",iconColor:"#FF6B35",guideCount:1,difficulty:2,tags:["Archery","IO","Pixel"],description:"Pixel archery combat with skill upgrades and leaderboard ranking."},
    {gameId:"bonk-io",name:"Bonk.io",id:"bonk-io",slug:"bonk-io",icon:"⚽",iconColor:"#2196F3",guideCount:1,difficulty:3,tags:["Physics","Multiplayer","Classic"],description:"Physics-based multiplayer ball combat game."},
    {gameId:"ev-io",name:"Ev.io",id:"ev-io",slug:"ev-io",icon:"🔫",iconColor:"#00BCD4",guideCount:1,difficulty:3,tags:["FPS","Cyberpunk","Blockchain"],description:"Cyberpunk browser FPS with play-to-earn mechanics. Choose weapons, customize abilities, and dominate the arena."},
    {gameId:"schoolbreak-io",name:"SchoolBreak.io",id:"schoolbreak-io",slug:"schoolbreak-io",icon:"🎒",iconColor:"#FF9800",guideCount:1,difficulty:2,tags:["Asymmetric","Party","Multiplayer"],description:"Student vs Teacher chaos! Cause mayhem or enforce discipline in this unique asymmetric multiplayer game."},
    {gameId:"florr-io",name:"Florr.io",id:"florr-io",slug:"florr-io",icon:"🌸",iconColor:"#E91E63",guideCount:1,difficulty:4,tags:["Flower","Crafting","PvP","Farming"],description:"Unique multiplayer .io game where you play as a flower with orbiting petals. Collect, craft, and battle through diverse biomes."},
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
    },

    {
        id: 'devast-io',
        name: 'Devast.io',
        icon: '☢️',
        iconColor: '#4CAF50',
        guideCount: 1,
        difficulty: 4,
        tags: ['Survival', 'Crafting', 'Base Building', 'PvP'],
        description: 'Post-apocalyptic survival io game with resource gathering, base building, crafting, and radioactive wasteland combat.'
    },
    {
        id: 'betrayal-io',
        name: 'Betrayal.io',
        icon: '🕵️',
        iconColor: '#673AB7',
        guideCount: 1,
        difficulty: 3,
        tags: ['Social Deduction', 'Multiplayer', 'Party', 'Deception'],
        description: 'Browser-based social deduction game where crewmates complete tasks while betrayers sabotage and deceive.'
    },
    {
    id: 'snake-io',
    name: 'Snake.io',
    icon: '🐍',
    iconColor: '#4CAF50',
    guideCount: 1,
    difficulty: 2,
    tags: ["Arcade", "Casual"],
    description: 'Classic snake game where you grow by eating pellets and avoid collisions.'
    },
    {
    id: 'flyordie-io',
    name: 'FlyOrDie.io',
    icon: '🪰',
    iconColor: '#FF6F00',
    guideCount: 1,
    difficulty: 3,
    tags: ["Survival", "Multiplayer", "Arcade"],
    description: 'Start as a fly and evolve into stronger creatures in this multiplayer survival game.'
    },
    {
    id: 'limax-io',
    name: 'Limax.io',
    icon: '🐍',
    iconColor: '#7B68EE',
    guideCount: 1,
    difficulty: 3,
    tags: ["Arena", "PvP", "Action"],
    description: 'A competitive arena game where players control neon snakes and battle for dominance.'
    },
    {
    id: 'a-slithery-snake-and-snowball-io',
    name: 'A Slithery Snake and Snowball.io',
    icon: '🐍',
    iconColor: '#87CEEB',
    guideCount: 1,
    difficulty: 2,
    tags: ["arcade", "multiplayer", "action"],
    description: 'Control a slithery snake to collect snowballs and grow longer while avoiding other players in this winter-themed arena.'
    },
    {
    id: 'aipaperanimals-io',
    name: 'AIPaperAnimals.io',
    icon: '🐰',
    iconColor: '#FFB6C1',
    guideCount: 1,
    difficulty: 2,
    tags: ["casual", "multiplayer", "paper"],
    description: 'Control adorable AI-powered paper animals in a competitive arena where you collect supplies and avoid elimination.'
    },
    {
    id: 'arras-io',
    name: 'Arras.io',
    icon: '🔫',
    iconColor: '#FF6B6B',
    guideCount: 1,
    difficulty: 3,
    tags: ["Tank Game", "Multiplayer", "Action"],
    description: 'Control a tank in an arena and battle against other players in this top-down shooter.'
    },
    {
    id: 'amogus-io',
    name: 'Amogus.io',
    icon: '🚀',
    iconColor: '#FF3D3D',
    guideCount: 1,
    difficulty: 3,
    tags: ["Multiplayer", "Action"],
    description: 'A multiplayer browser game where players complete tasks and identify impostors among them.'
    },
    {
    id: 'agma-io',
    name: 'Agma.io',
    icon: '🧬',
    iconColor: '#7B68EE',
    guideCount: 1,
    difficulty: 3,
    tags: ["Survival", "Multiplayer", "Cellular"],
    description: 'A multiplayer browser game where players control cells or organisms, consume resources, and grow larger while avoiding predators in a competitive arena.'
    },
    {
        id: 'aquapark-io',
        name: 'AquaPark.io',
        icon: '🌊',
        iconColor: '#00bcd4',
        guideCount: 1,
        difficulty: 2,
        tags: ['Racing', 'Water', 'Multiplayer'],
        description: 'Race down giant water slides, bump rivals, and master shortcut jumps.'
    },
    {
    id: 'arena-io',
    name: 'Arena.io',
    icon: '⚔️',
    iconColor: '#E74C3C',
    guideCount: 1,
    difficulty: 2,
    tags: ["action", "multiplayer", "battle"],
    description: 'Battle against other players in a fast-paced arena, collecting power-ups and eliminating opponents to become the last one standing.'
    },
    {
    id: 'brutal-io',
    name: 'Brutal.io',
    icon: '⚔️',
    iconColor: '#E74C3C',
    guideCount: 1,
    difficulty: 3,
    tags: ["Action", "Multiplayer", "Combat"],
    description: 'Battle other players using melee weapons in a fast-paced arena combat game.'
    },
    {
    id: 'battledudes-io',
    name: 'BattleDudes.io',
    icon: '⚔️',
    iconColor: '#FF6B6B',
    guideCount: 1,
    difficulty: 3,
    tags: ["battle", "multiplayer", "action"],
    description: 'Battle against other players in fast-paced arena combat with customizable characters and weapons.'
    },
    
    {
    id: 'archers-io',
    name: 'Archers.io',
    icon: '🏹',
    iconColor: '#E74C3C',
    guideCount: 1,
    difficulty: 2,
    tags: ["action", "multiplayer", "archery"],
    description: 'Control an archer in an arena, shoot arrows at opponents, and survive as long as possible.'
    },
    {
    id: 'basketball-io',
    name: 'Basketball.io',
    icon: '🏀',
    iconColor: '#FF6B35',
    guideCount: 1,
    difficulty: 2,
    tags: ["Sports", "Multiplayer", "Action"],
    description: 'Compete against other players in fast-paced basketball matches to score baskets and dominate the arena.'
    },
    {
    id: 'boxer-io',
    name: 'Boxer.io',
    icon: '🥊',
    iconColor: '#DC143C',
    guideCount: 1,
    difficulty: 3,
    tags: ["multiplayer", "action", "fighting"],
    description: 'A fast-paced multiplayer boxing game where you battle against other players to become the ultimate champion.'
    },
    {
    id: 'axes-io',
    name: 'AXES.io',
    icon: '🪓',
    iconColor: '#FF4500',
    guideCount: 1,
    difficulty: 3,
    tags: ["action", "battle-royale", "multiplayer"],
    description: 'Throw axes at opponents in fast-paced arena combat as you try to survive and become the last player standing.'
    },
    {
    id: 'axe-io',
    name: 'Axe.io',
    icon: '🪓',
    iconColor: '#8B5A2B',
    guideCount: 1,
    difficulty: 2,
    tags: ["multiplayer", "action", "battle"],
    description: 'Throw axes at opponents in fast-paced multiplayer arena combat.'
    },
    {
    id: 'bighole-io',
    name: 'BigHole.io',
    icon: '🕳️',
    iconColor: '#2C3E50',
    guideCount: 1,
    difficulty: 2,
    tags: ["casual", "arcade", "consumption"],
    description: 'Control a growing black hole that swallows objects and debris to become the biggest hole on the map.'
    },
    {
    id: 'bruh-io',
    name: 'Bruh.io',
    icon: '😎',
    iconColor: '#FFD93D',
    guideCount: 1,
    difficulty: 2,
    tags: ["casual", "multiplayer", "action"],
    description: 'A casual multiplayer action game where players compete to survive and outplay opponents in fast-paced matches.'
    },
    {
    id: 'brosswordz-io',
    name: 'BrosSwordz.io',
    icon: '⚔️',
    iconColor: '#FF4500',
    guideCount: 1,
    difficulty: 3,
    tags: ["Combat", "Fighting", "Multiplayer"],
    description: 'Fast-paced multiplayer sword battle arena where players fight against each other using various sword weapons.'
    },
    {
    id: 'basketbros-io',
    name: 'BasketBros.io',
    icon: '🏀',
    iconColor: '#FF8C00',
    guideCount: 1,
    difficulty: 2,
    tags: ["Sports", "Basketball", "Multiplayer"],
    description: 'Compete in fast-paced 1v1 or 2v2 arcade basketball matches against players from around the world.'
    },
    {
    id: 'buildroyale-io',
    name: 'BuildRoyale.io',
    icon: '🏗️',
    iconColor: '#FF9800',
    guideCount: 1,
    difficulty: 3,
    tags: ["Building", "Battle Royale", "Shooter"],
    description: 'Build structures to defend yourself and fight to be the last player standing in this browser-based battle royale game.'
    },
    {
    id: 'copter-io',
    name: 'Copter.io',
    icon: '🚁',
    iconColor: '#4CAF50',
    guideCount: 1,
    difficulty: 3,
    tags: ["arcade", "endless-runner", "skill"],
    description: 'Navigate a helicopter through an endless, obstacle-filled cave while collecting coins and avoiding crashes.'
    },
    {
    id: 'battlepoint-io',
    name: 'Battlepoint.io',
    icon: '🎯',
    iconColor: '#FF4500',
    guideCount: 1,
    difficulty: 3,
    tags: ["Shooter", "Action", "Multiplayer"],
    description: 'A fast-paced multiplayer top-down shooter where players battle to dominate the arena.'
    },
    {
    id: 'braains-io',
    name: 'Braains.io',
    icon: '🧠',
    iconColor: '#D32F2F',
    guideCount: 1,
    difficulty: 3,
    tags: ["Zombie", "Survival", "Multiplayer"],
    description: 'Play as a zombie hunting humans for their brains or survive the horde as a human in this multiplayer game.'
    },
    {
    id: 'aquar-io',
    name: 'Aquar.io',
    icon: '🐠',
    iconColor: '#00BFFF',
    guideCount: 1,
    difficulty: 2,
    tags: ["aquarium", "evolution", "casual"],
    description: 'Feed smaller fish to grow and evolve into larger marine creatures in a competitive aquarium ecosystem.'
    },
    {
    id: 'babyshark-io',
    name: 'BabyShark.io',
    icon: '🦈',
    iconColor: '#00B4D8',
    guideCount: 1,
    difficulty: 2,
    tags: ["arcade", "multiplayer", "animal"],
    description: 'Swim around the ocean as a baby shark, eating smaller fish to grow while avoiding larger predators.'
    },
    {
    id: 'bombom-io',
    name: 'BomBom.io',
    icon: '💣',
    iconColor: '#FF5722',
    guideCount: 1,
    difficulty: 3,
    tags: ["Action", "Multiplayer", "Arcade"],
    description: 'Place bombs strategically to eliminate other players and be the last one standing in an explosive multiplayer arena.'
    },
    {
    id: 'block-io',
    name: 'Block.io',
    icon: '🧱',
    iconColor: '#2ECC71',
    guideCount: 1,
    difficulty: 2,
    tags: ["arcade", "multiplayer", "sandbox"],
    description: 'Compete against other players to build structures and capture territory in a blocky voxel arena.'
    },
    {
    id: 'animal-io',
    name: 'Animal.io',
    icon: '🐾',
    iconColor: '#4CAF50',
    guideCount: 1,
    difficulty: 2,
    tags: ["casual", "multiplayer", "animal"],
    description: 'Evolve your animal by eating smaller creatures and avoiding predators in a massive multiplayer ecosystem.'
    },
    {
    id: 'battle-io',
    name: 'Battle.io',
    icon: '⚔️',
    iconColor: '#FF5722',
    guideCount: 1,
    difficulty: 3,
    tags: ["Action", "Shooter", "Battle Royale"],
    description: 'A fast-paced multiplayer battle arena where players fight with weapons and vehicles to be the last one standing.'
    },
    {
    id: 'zombs-royale-io',
    name: 'ZombsRoyale.io',
    icon: '🪂',
    iconColor: '#ff6b35',
    guideCount: 1,
    difficulty: 4,
    tags: ["Shooter", "Battle Royale", "Action"],
    description: '100-player 2D top-down battle royale. Parachute in, loot weapons, survive the gas, and be the last one standing.'
    },
    {
    id: 'battletabs-io',
    name: 'BattleTabs.io',
    icon: '⚔️',
    iconColor: '#8A2BE2',
    guideCount: 1,
    difficulty: 2,
    tags: ["Auto-Battler", "RPG", "Idle"],
    description: 'Collect and upgrade unique characters to automatically battle enemies and conquer realms.'
    },
    {
    id: 'bloxdhop-io',
    name: 'BloxdHop.io',
    icon: '🧱',
    iconColor: '#FF9800',
    guideCount: 1,
    difficulty: 3,
    tags: ["Platformer", "Parkour", "Arcade"],
    description: 'Jump across blocky platforms and avoid obstacles in this fast-paced parkour game.'
    },
    {
    id: 'brainrots-io',
    name: 'Brainrots.io',
    icon: '🧠',
    iconColor: '#FF00FF',
    guideCount: 1,
    difficulty: 2,
    tags: ["Meme", "Casual", "Arcade"],
    description: 'Absorb smaller meme entities and grow your brainrot collection in a chaotic multiplayer arena.'
    },
    {
    id: 'battleboats-io',
    name: 'Battleboats.io',
    icon: '🚢',
    iconColor: '#1E90FF',
    guideCount: 1,
    difficulty: 3,
    tags: ["Multiplayer", "Strategy", "Naval"],
    description: 'Sink your opponents\' fleets in a real-time multiplayer naval strategy game based on the classic game of Battleship.'
    },
    {
    id: 'adventuremoomoo-io',
    name: 'AdventureMoomoo.io',
    icon: '🐮',
    iconColor: '#8B4513',
    guideCount: 1,
    difficulty: 2,
    tags: ["Survival", "Crafting", "Multiplayer"],
    description: 'Gather resources, craft weapons, and build villages to survive in a multiplayer animal sandbox world.'
    },
    {
    id: 'badegg-io',
    name: 'Badegg.io',
    icon: '🥚',
    iconColor: '#FFD700',
    guideCount: 1,
    difficulty: 2,
    tags: ["Physics", "Arena", "Action"],
    description: 'Push other eggs out of the arena using physics-based collisions to be the last egg standing.'
    },
    {
    id: 'battles-io',
    name: 'Battles.io',
    icon: '⚔️',
    iconColor: '#E74C3C',
    guideCount: 1,
    difficulty: 3,
    tags: ["Action", "Multiplayer", "Arena"],
    description: 'Engage in fast-paced multiplayer combat and battle against players worldwide in an arena.'
    },
    {
    id: 'battlefields-io',
    name: 'Battlefields.io',
    icon: '🪖',
    iconColor: '#556B2F',
    guideCount: 1,
    difficulty: 3,
    tags: ["Action", "Multiplayer", "Strategy"],
    description: 'Engage in intense multiplayer combat, commanding tanks and troops to conquer territories and defeat rival players.'
    },
    {
    id: 'alis-io',
    name: 'Alis.io',
    icon: '🪽',
    iconColor: '#4A90E2',
    guideCount: 1,
    difficulty: 2,
    tags: ["Arcade", "Multiplayer", "Action"],
    description: 'Fly through the sky and battle other players in this fast-paced aerial combat arena.'
    },
    {
    id: 'bladers-io',
    name: 'Bladers.io',
    icon: '🛼',
    iconColor: '#4FC3F7',
    guideCount: 1,
    difficulty: 2,
    tags: ["io", "action", "skating"],
    description: 'Skate on ice, perform tricks, and battle other players in a fast-paced multiplayer arena.'
    },
    {
    id: 'antwar-io',
    name: 'AntWar.io',
    icon: '🐜',
    iconColor: '#8B4513',
    guideCount: 1,
    difficulty: 3,
    tags: ["Strategy", "Multiplayer", "Action"],
    description: 'Build and manage your ant colony while battling other players to control the territory.'
    },
    {
    id: 'bopz-io',
    name: 'BOPZ.io',
    icon: '👊',
    iconColor: '#FF5722',
    guideCount: 1,
    difficulty: 3,
    tags: ["action", "arena", "multiplayer"],
    description: 'Hit and knock out other players in a fast-paced multiplayer arena to claim the top spot on the leaderboard.'
    },
    {
    id: 'battlegrounds-io',
    name: 'Battlegrounds.io',
    icon: '🎯',
    iconColor: '#556B2F',
    guideCount: 1,
    difficulty: 3,
    tags: ["battle-royale", "shooter", "multiplayer"],
    description: 'A fast-paced multiplayer battle royale where players scavenge for weapons and fight to be the last one standing.'
    },
    {
    id: 'bighero-io',
    name: 'BigHero.io',
    icon: '🦸',
    iconColor: '#FF4500',
    guideCount: 1,
    difficulty: 2,
    tags: ["action", "superhero", "arena"],
    description: 'Battle other players in a superhero arena using unique abilities and power-ups to become the ultimate hero.'
    },
    {
    id: 'airwings-io',
    name: 'AirWings.io',
    icon: '✈️',
    iconColor: '#4A90E2',
    guideCount: 1,
    difficulty: 3,
    tags: ["action", "shooter", "multiplayer"],
    description: 'Engage in intense aerial dogfights and dominate the skies in this fast-paced multiplayer combat game.'
    },
    {
    id: 'bombhopper-io',
    name: 'BombHopper.io',
    icon: '💣',
    iconColor: '#FF5722',
    guideCount: 1,
    difficulty: 3,
    tags: ["Physics", "Platformer", "Action"],
    description: 'Use the recoil from exploding bombs to blast yourself through physics-based platforming levels and reach the goal.'
    },
    {
    id: 'armedforces-io',
    name: 'ArmedForces.io',
    icon: '🪖',
    iconColor: '#4B5320',
    guideCount: 1,
    difficulty: 3,
    tags: ["Shooter", "Multiplayer", "Action"],
    description: 'A team-based military shooter where you select your class and battle against other players in fast-paced arenas.'
    },
    {
    id: 'beetles-io',
    name: 'Beetles.io',
    icon: '🪲',
    iconColor: '#2E8B57',
    guideCount: 1,
    difficulty: 2,
    tags: ["Action", "Survival", "Multiplayer"],
    description: 'Control a beetle, eat to grow, and defeat other players in a competitive insect survival arena.'
    },
    {
    id: 'carfight-io',
    name: 'CarFight.io',
    icon: '🏎️',
    iconColor: '#FF4500',
    guideCount: 1,
    difficulty: 3,
    tags: ["action", "combat", "multiplayer"],
    description: 'Battle other players in explosive vehicular combat arenas to destroy opponents and dominate the battlefield.'
    },
    {
    id: 'bist-io',
    name: 'Bist.io',
    icon: '🎖️',
    iconColor: '#4CAF50',
    guideCount: 1,
    difficulty: 3,
    tags: ["Tank", "Action", "Multiplayer"],
    description: 'Drive your tank, collect stars, and dominate the multiplayer battle arena.'
    },
    {
    id: 'cavegame-io',
    name: 'Cavegame.io',
    icon: '⛰️',
    iconColor: '#8B4513',
    guideCount: 1,
    difficulty: 3,
    tags: ["Survival", "Crafting", "Multiplayer"],
    description: 'A 2D multiplayer survival game inspired by Minecraft where players mine resources, craft weapons, build bases, and engage in PvP combat.'
    },
    {
    id: 'bubbleman-io',
    name: 'Bubbleman.io',
    icon: '🫧',
    iconColor: '#FF6B6B',
    guideCount: 1,
    difficulty: 2,
    tags: ["Action", "IO", "Arcade"],
    description: 'Players drag left and right to control their character, punching colorful enemies to score points and gain time within 30-second rounds, while collecting orbs to grow bigger.'
    },
    {
    id: 'anguis-io',
    name: 'Anguis.io',
    icon: '🐍',
    iconColor: '#9D4EDD',
    guideCount: 1,
    difficulty: 2,
    tags: ["snake", "multiplayer", "io"],
    description: 'A competitive multiplayer snake game where you control a growing snake in a shared arena, collecting orbs to get bigger while avoiding collisions with other players.'
    },
    {
    id: 'astrodud-io',
    name: 'Astrodud.io',
    icon: '🧑‍🚀',
    iconColor: '#0B3D91',
    guideCount: 1,
    difficulty: 2,
    tags: ["obstacle-course", "multiplayer", "racing"],
    description: 'Control a tiny astronaut in a chaotic multiplayer obstacle course survival race, navigating hazards like pitfalls and swinging bats to be the last one standing.'
    },
    {
    id: 'cellcraft-io',
    name: 'Cellcraft.io',
    icon: '🦠',
    iconColor: '#4CAF50',
    guideCount: 1,
    difficulty: 2,
    tags: ["io", "multiplayer", "arcade"],
    description: 'Control a blob to consume food and other players to grow, earn XP, and collect coins to craft powerful upgrades in a competitive arena.'
    },
    {
    id: 'candy-io',
    name: 'Candy.io',
    icon: '🍬',
    iconColor: '#FF69B4',
    guideCount: 1,
    difficulty: 2,
    tags: ["io", "casual"],
    description: 'The search results provided are empty, and there is no widely documented .io game specifically titled \'Candy.io\' with verifiable mechanics, so the actual core gameplay cannot be described without guessing.'
    },
    {
    id: 'bball-io',
    name: 'BBall.io',
    icon: '🏀',
    iconColor: '#FF8C00',
    guideCount: 1,
    difficulty: 2,
    tags: ["Sports", "Multiplayer", "Basketball"],
    description: 'A fast-paced 3D multiplayer basketball game where you control a single player to sprint, dribble, pass, and dunk against live opponents on a small-sided court.'
    },
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
    difficulty: 5,
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
        difficulty: 5,
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
        difficulty: 3,
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
        difficulty: 3,
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
        difficulty: 3
    },
    {
        id: 'superhex-io-guide',
        title: 'Superhex.io Guide: Claim Territory & Defend Your Hex',
        game: 'Superhex.io',
        gameId: 'superhex-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Superhex.io territory control strategies, hex claiming mechanics, and defense tactics to dominate the map.',
        difficulty: 3
    },
    {
        id: 'voxelim-io-guide',
        title: 'Voxelim.io Guide: Build & Battle in a Voxel World',
        game: 'Voxelim.io',
        gameId: 'voxelim-io',
        date: '2026-06-13',
        readTime: '9 min',
        excerpt: 'Master Voxelim.io voxel building mechanics, combat strategies, and resource gathering for battlefield domination.',
        difficulty: 3
    },
    {
        id: 'warden-io-guide',
        title: 'Warden.io Guide: Dungeon Crawler Strategy & Boss Tips',
        game: 'Warden.io',
        gameId: 'warden-io',
        date: '2026-06-13',
        readTime: '9 min',
        excerpt: 'Master Warden.io dungeon crawling strategies, boss fight tactics, and class builds for the mystical arena.',
        difficulty: 3
    },
    {
        id: 'wormate-io-guide',
        title: 'Wormate.io Guide: Sweet Treats & Giant Worms',
        game: 'Wormate.io',
        gameId: 'wormate-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Wormate.io sweet food collection, worm upgrades, and arena tactics for growth and survival.',
        difficulty: 1
    },
    {
        id: 'wormax-io-guide',
        title: 'Wormax.io Guide: Slither Smart & Grow Massive',
        game: 'Wormax.io',
        gameId: 'wormax-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Wormax.io smart slithering, boost mastery, and strategies to become the biggest worm on the server.',
        difficulty: 1
    },
    {
        id: 'zapper-io-guide',
        title: 'Zapper.io Guide: Lightning-Fast Combat Tips',
        game: 'Zapper.io',
        gameId: 'zapper-io',
        date: '2026-06-13',
        readTime: '8 min',
        excerpt: 'Master Zapper.io lightning combat tactics, movement strategies, and weapon upgrades to dominate the arena.',
        difficulty: 3
    },
    {
        id: 'bonk-io-guide',
        title: 'Bonk.io Guide: Master Physics Combat & Knockouts',
        game: 'Bonk.io',
        gameId: 'bonk-io',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master Bonk.io with our complete guide. Learn physics mechanics, heavy mode timing, map strategies, and pro tips to knock every opponent off.',
        difficulty: 3
    },
    {
        id: 'nobrakes-io-guide',
        title: 'NoBrakes.io Guide: Drift, Boost & Race to First',
        game: 'NoBrakes.io',
        gameId: 'nobrakes-io',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master NoBrakes.io with our complete guide. Learn drift mechanics, boost timing, track shortcuts, and racing strategies to leave your opponents in the dust.',
        difficulty: 1
    },
    {
        id: 'liquid-swarm-guide',
        title: 'Liquid Swarm Guide: Master the Ultimate Consuming Force',
        game: 'Liquid Swarm',
        gameId: 'liquid-swarm',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master Liquid Swarm with this complete guide. Learn the surround mechanic, power-up strategies, and pro tips to become the ultimate consuming force.',
        difficulty: 1
    },
    {
        id: 'venge-io-guide',
        title: 'Venge.io Guide: Master FPS Arena Combat',
        game: 'Venge.io',
        gameId: 'venge-io',
        date: '2026-06-11',
        readTime: '10 min',
        excerpt: 'Master Venge.io with this complete guide. Covers controls, hero abilities, game modes, and top strategies to dominate the arena.',
        difficulty: 1
    },
    {
        id: 'zombsroyale-io-guide',
        title: 'ZombsRoyale.io Complete Guide: Battle Royale Tactics',
        game: 'ZombsRoyale.io',
        gameId: 'zombsroyale-io',
        date: '2026-06-11',
        readTime: '10 min',
        excerpt: 'Master battle royale tactics in ZombsRoyale.io. Learn landing strategies, weapon selection, combat tips, and circle control to become the last survivor.',
        difficulty: 1
    },
    {
        id: 'evowars-io-guide',
        title: 'EvoWars.io Complete Guide 2024: Master Evolution \u0026 Combat',
        game: 'EvoWars.io',
        gameId: 'evowars-io',
        date: '2026-06-09',
        readTime: '9 min',
        excerpt: 'Master evolution mechanics, food chain strategies, and predator-prey tactics to become the apex predator.',
        difficulty: 1
    },
    {
        id: 'lordz-io-guide',
        title: 'Lordz.io Guide: Build Your Medieval Empire and Conquer the Battlefield',
        game: 'Lordz.io',
        gameId: 'lordz-io',
        date: '2026-06-12',
        readTime: '8 min',
        excerpt: 'Master Lordz.io with our complete guide. Learn unit stats, economy strategy, army composition, and pro tips to dominate the medieval battlefield.',
        difficulty: 3,
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
        difficulty: 3,
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
        difficulty: 1
    },
    {
        id: 'taming-io-guide',
        title: 'Taming.io Guide: Master Pet Taming & Base Building',
        game: 'Taming.io',
        gameId: 'taming-io',
        date: '2026-06-07',
        readTime: '10 min',
        excerpt: 'Build your ultimate pet army! Learn pet taming mechanics, base defense, elemental combat, and climb the leaderboard.',
        difficulty: 1
    },
    {
        id: 'stickman-hook-guide',
        title: 'Stickman Hook Guide: Master the Swing & Conquer Every Level',
        game: 'Stickman Hook',
        gameId: 'stickman-hook',
        date: '2026-06-16',
        readTime: '8 min',
        excerpt: 'Master swinging mechanics, release timing, level strategies, and pro tips to dominate every stage in Stickman Hook.',
        difficulty: 1
    },
    {
        id: 'krunker-io-guide',
        title: 'Krunker.io Guide: Master FPS Combat & Movement',
        game: 'Krunker.io',
        gameId: 'krunker-io',
        date: '2026-06-05',
        readTime: '12 min',
        excerpt: 'Master FPS combat tactics, movement strategies, class selection, weapon tips, and dominate the battlefield in Krunker.io.',
        difficulty: 3
    },
    {
        id: 'diep-io-guide',
        title: 'Diep.io Complete Guide: Master Tank Combat & Upgrades',
        game: 'Diep.io',
        gameId: 'diep-io',
        date: '2026-05-27',
        readTime: '16 min',
        excerpt: 'Master tank combat, upgrade paths, best builds for every class, and dominate the battlefield in Diep.io.',
        difficulty: 3
    },
    {
        id: 'defly-io-guide',
        title: 'Defly.io Guide: Build, Defend & Conquer',
        game: 'Defly.io',
        gameId: 'defly-io',
        date: '2026-05-20',
        readTime: '9 min',
        excerpt: 'Master territory control, helicopter combat, defensive building, and top strategies to dominate the leaderboard.',
        difficulty: 1
    },
        {
        id: 'brutalmania-io-guide',
        title: 'BrutalMania.io Guide: Arena Combat Tips & Weapon Strategy',
        game: 'BrutalMania.io',
        gameId: 'brutalmania-io',
        date: '2026-05-15',
        readTime: '9 min',
        excerpt: 'Master arena combat tactics, weapon selection, movement strategies, and dominate the battleground.',
        difficulty: 1
    },
    {
        id: 'swordz-io-guide',
        title: 'Swordz.io Complete Guide: Master Medieval Combat',
        game: 'Swordz.io',
        gameId: 'swordz-io',
        date: '2026-05-16',
        readTime: '10 min',
        excerpt: 'Master sword combat, dash mechanics, positioning, and climbing the leaderboard.',
        difficulty: 1
    },
    {
        id: 'medieval-io-guide',
        title: 'Medieval.io Complete Guide: Battle Strategies & Hero Guide',
        game: 'Medieval.io',
        gameId: 'medieval-io',
        date: '2026-05-16',
        readTime: '11 min',
        excerpt: 'Dominate the 8-player arena with hero selection, army management, and advanced tactics.',
        difficulty: 1
    },
    {
        id: 'agar-io-advanced-guide',
        title: 'Agar.io Advanced Guide: Pro Split Tricks & Late Game Strategy',
        game: 'Agar.io',
        gameId: 'agar-io',
        date: '2026-05-14',
        readTime: '10 min',
        excerpt: 'Master pro split tricks, micro-techniques, late game dominance, and high-level strategies.',
        difficulty: 5
    },
    {
        id: 'smashkarts-io-guide',
        title: 'SmashKarts.io Guide: Master Kart Combat',
        game: 'SmashKarts.io',
        gameId: 'smashkarts-io',
        date: '2026-05-12',
        readTime: '11 min',
        excerpt: 'Learn weapon strategies, map control, driving tips, and pro tactics to dominate the leaderboard.',
        difficulty: 3
    },
    {
        id: 'surviv-io-guide',
        title: 'Surviv.io Complete Guide: Master 2D Battle Royale',
        game: 'Surviv.io',
        gameId: 'surviv-io',
        date: '2024-01-15',
        readTime: '14 min',
        excerpt: 'Learn weapons, map strategies, and survival tactics to become the last survivor.',
        difficulty: 3
    },
    {
        id: 'bloxd-io-guide',
        title: 'Bloxd.io Complete Guide: Bedwars, Parkour & PvP',
        game: 'Bloxd.io',
        gameId: 'bloxd-io',
        date: '2026-05-25',
        readTime: '13 min',
        excerpt: 'Master all game modes including Bedwars strategies, building mechanics, and PvP combat.',
        difficulty: 3
    },
    {
        id: 'crazysteve-io-guide',
        title: 'CrazySteve.io Guide: Block-Building Battle Royale',
        game: 'CrazySteve.io',
        gameId: 'crazysteve-io',
        date: '2026-05-16',
        readTime: '10 min',
        excerpt: 'Master block-building combat strategies and battle royale survival tactics in CrazySteve.io.',
        difficulty: 1
    },
    {
        id: 'curser-io-guide',
        title: 'Curser.io Guide: Navigate & Survive the Cursor Wars',
        game: 'Curser.io',
        gameId: 'curser-io',
        date: '2026-05-17',
        readTime: '7 min',
        excerpt: 'Master cursor movement, survival tactics, and browser battlefield navigation in Curser.io.',
        difficulty: 1
    },
    {
        id: 'blumgi-rocket-guide',
        title: 'Blumgi Rocket Guide: Launch, Fly & Land Perfectly',
        game: 'Blumgi Rocket',
        gameId: 'blumgi-rocket',
        date: '2026-05-19',
        readTime: '9 min',
        excerpt: 'Master rocket launch mechanics, trajectory prediction, and precision landing in Blumgi Rocket.',
        difficulty: 3
    },
    {
        id: 'shell-shockers-guide',
        title: 'Shell Shockers Complete Guide: Best Classes & Weapons',
        game: 'Shell Shockers',
        gameId: 'shell-shockers',
        date: '2024-01-15',
        readTime: '12 min',
        excerpt: 'Learn class selection, weapon comparisons, and map strategies for egg combat.',
        difficulty: 3
    },
    {
        id: 'mope-io-guide',
        title: 'Mope.io Complete Guide: Animal Evolution & Survival',
        game: 'Mope.io',
        gameId: 'mope-io',
        date: '2024-01-15',
        readTime: '13 min',
        excerpt: 'Master animal evolution routes, food chain strategies, and survival tips.',
        difficulty: 1
    },
    {
        id: 'gartic-io-guide',
        title: 'Gartic.io Complete Guide: Drawing & Guessing Tips',
        game: 'Gartic.io',
        gameId: 'gartic-io',
        date: '2024-01-15',
        readTime: '11 min',
        excerpt: 'Master drawing techniques, guessing strategies, and room settings.',
        difficulty: 1
    },
    {
        id: 'wings-io-guide',
        title: 'Wings.io: 6 Fatal Mistakes Killing Your Dogfights (And How to Fix Them)',
        game: 'Wings.io',
        gameId: 'wings-io',
        date: '2026-08-15',
        readTime: '10 min',
        excerpt: 'Stop dying early in Wings.io. A competitive veteran breaks down the 6 fatal mistakes ruining your aerial runs and exactly how to fix each one.',
        difficulty: 3
    },
    {
        id: 'moomoo-io-guide',
        title: 'MooMoo.io Complete Guide: Base Building & Survival',
        game: 'MooMoo.io',
        gameId: 'moomoo-io',
        date: '2024-01-15',
        readTime: '12 min',
        excerpt: 'Master base designs, resource management, and PvP defense strategies.',
        difficulty: 3
    },
    {
        id: 'slither-io-boosting',
        title: 'Mastering Boost in Slither.io: Timing and Tactics',
        game: 'Slither.io',
        gameId: 'slither-io',
        date: '2024-01-12',
        readTime: '6 min',
        excerpt: 'The complete guide to using boost strategically without crashing.',
        difficulty: 3
    },
    {
        id: 'diep-io-tanks',
        title: 'Diep.io Tank Builds Tier List 2024',
        game: 'Diep.io',
        gameId: 'diep-io',
        date: '2024-01-10',
        readTime: '12 min',
        excerpt: 'Discover the best tank builds and upgrades for domination.',
        difficulty: 5
    },
    {
        id: 'defend-io-guide',
        title: 'Defend.io Guide: Tower Defense Strategy & Tips',
        game: 'Defend.io',
        gameId: 'defend-io',
        date: '2026-05-22',
        readTime: '8 min',
        excerpt: 'Master tower placement, upgrade strategies, and wave defense tactics in Defend.io.',
        difficulty: 1
    },
    {
        id: 'hole-io-guide',
        title: 'Hole.io Guide: Grow, Swallow & Dominate the City',
        game: 'Hole.io',
        gameId: 'hole-io',
        date: '2026-05-21',
        readTime: '8 min',
        excerpt: 'Master city swallowing, vehicle chasing, map control, and absorbing smaller holes in Hole.io.',
        difficulty: 1
    },
    {
        id: 'paper-io-guide',
        title: 'Paper.io Guide: Claim Territory & Defend Your Zone',
        game: 'Paper.io',
        gameId: 'paper-io',
        date: '2026-05-20',
        readTime: '8 min',
        excerpt: 'Master territory claiming, zone defense, and trail-cutting strategies in Paper.io.',
        difficulty: 1
    },
    {
        id: 'dogod-io-guide',
        title: 'Dogod.io Guide: Evolve & Dominate the Food Chain',
        game: 'Dogod.io',
        gameId: 'dogod-io',
        date: '2026-05-23',
        readTime: '9 min',
        excerpt: 'Master evolution mechanics, food chain strategies, and predator-prey tactics to become the apex predator.',
        difficulty: 1
    },
    {
        id: 'angry-worms-io-guide',
        title: 'Angry Worms.io Guide: Master the Slither-Style Arena',
        game: 'Angry Worms.io',
        gameId: 'angry-worms-io',
        date: '2026-05-24',
        readTime: '11 min',
        excerpt: 'Proven strategies to grow your worm and dominate the Angry Worms.io arena. From basic controls to advanced traps.',
        difficulty: 1
    },
    {
        id: 'repuls-io-guide',
        title: 'Repuls.io Guide: FPS Combat & Map Control',
        game: 'Repuls.io',
        gameId: 'repuls-io',
        date: '2026-05-26',
        readTime: '10 min',
        excerpt: 'Master the unique repulsion launcher mechanics, weapon loadouts, and tactical movement in this fast-paced FPS arena shooter.',
        difficulty: 3
    },
    {
        id: 'spawner-io-guide',
        title: 'Spawner.io Guide: Build Defenses & Survive',
        game: 'Spawner.io',
        gameId: 'spawner-io',
        date: '2026-05-28',
        readTime: '8 min',
        excerpt: 'Master block spawning, defense building, and survival tactics in this unique tower defense .io game.',
        difficulty: 1
    },
    {
        id: 'gulper-io-guide',
        title: 'Gulper.io Guide: Grow Big & Dominate the Arena',
        game: 'Gulper.io',
        gameId: 'gulper-io',
        date: '2026-05-29',
        readTime: '10 min',
        excerpt: 'Master the gulper mechanics, grow your creature, eat opponents, and climb the leaderboard with proven strategies.',
        difficulty: 3
    },
    {
        id: 'spinner-io-guide',
        title: 'Spinner.io Guide: Spin to Win in the Arena',
        game: 'Spinner.io',
        gameId: 'spinner-io',
        date: '2026-05-30',
        readTime: '9 min',
        excerpt: 'Master spinning combat tactics, grow your spinner by defeating opponents, and dominate the arena with proven strategies.',
        difficulty: 3
    },
    {
        id: 'starblast-io-guide',
        title: 'Starblast.io Guide: Mine, Upgrade & Survive in Space',
        game: 'Starblast.io',
        gameId: 'starblast-io',
        date: '2026-05-30',
        readTime: '11 min',
        excerpt: 'Master spaceship upgrades, mining strategies, combat tactics, and survival tips in deep space battles.',
        difficulty: 3
    },
    {
        id: 'yohoho-io-guide',
        title: 'Yohoho.io Guide: Master Pirate Battle Royale',
        game: 'Yohoho.io',
        gameId: 'yohoho-io',
        date: '2026-05-31',
        readTime: '10 min',
        excerpt: 'Master pirate combat, collect coins, upgrade your ship, and become the ultimate pirate in Yohoho.io battle royale.',
        difficulty: 1
    },
    {
        id: 'snowball-io-guide',
        title: 'Snowball.io Guide: Roll, Throw & Knock Out',
        game: 'Snowball.io',
        gameId: 'snowball-io',
        date: '2026-05-31',
        readTime: '9 min',
        excerpt: 'Master snowball mechanics, push opponents off platforms, and dominate winter battles with proven strategies.',
        difficulty: 1
    },
    {
        id: 'goons-io-guide',
        title: 'Goons.io Guide: Sword Combat & Survival Tips',
        game: 'Goons.io',
        gameId: 'goons-io',
        date: '2026-06-03',
        readTime: '9 min',
        excerpt: 'Master sword combat tactics, block and dodge attacks, and survive medieval arena battles with proven strategies.',
        difficulty: 1
    },
    {
        id: 'littlebigsnake-io-guide',
        title: 'LittleBigSnake.io Guide: Fly, Grow & Dominate',
        game: 'LittleBigSnake.io',
        gameId: 'littlebigsnake-io',
        date: '2026-06-04',
        readTime: '9 min',
        excerpt: 'Master snake growth mechanics, evolve into flying dragonfly form, and dominate the food chain with proven strategies.',
        difficulty: 1
    },
    {
        id: 'sandboxels-guide',
        title: 'Sandboxels Guide: Master Physics Simulations',
        game: 'Sandboxels',
        gameId: 'sandboxels',
        date: '2026-06-06',
        readTime: '8 min',
        excerpt: 'Master element interactions, create amazing physics simulations, and explore 500+ elements in this creative sandbox game.',
        difficulty: 1
    },
    {
        id: 'poxel-io-guide',
        title: 'Poxel.io Guide: Master Weapons, Game Modes & Pixel FPS Tactics',
        game: 'Poxel.io',
        gameId: 'poxel-io',
        date: '2026-06-14',
        readTime: '10 min',
        excerpt: 'Master Poxel.io with our complete guide. Learn all 4 game modes, best weapon loadouts, map strategies, and pro tips to dominate the pixel FPS battlefield.',
        difficulty: 3,
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
        difficulty: 5,
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
        difficulty: 5,
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
        difficulty: 3,
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
        difficulty: 3,
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
        difficulty: 5,
        badge: '🏃'
    },
    {id:"ninja-io-guide",gameId:"ninja-io",name:"Ninja.io",title:"Ninja.io Guide: Master Weapons, Movement & Game Modes",date:"2026-06-21",difficulty: 5,readTime:11,url:"https://iogameguide.com/guides/ninja-io-guide",image:"https://iogameguide.com/images/games/ninja-io/hero.jpg"},
    {id:"arrow-arena-guide",gameId:"arrow-arena",name:"Arrow Arena",title:"Arrow Arena Guide: Master Archery Combat",date:"2026-06-21",difficulty:2,readTime:8,url:"https://iogameguide.com/guides/arrow-arena-guide",image:"https://iogameguide.com/images/games/arrow-arena/hero.jpg"},
    
    {id:"ev-io-guide",gameId:"ev-io",name:"Ev.io",title:"Ev.io Guide: Master Weapons, Abilities & Arena Combat",date:"2026-06-22",difficulty:3,readTime:8,url:"https://iogameguide.com/guides/ev-io-guide",image:"https://iogameguide.com/images/games/ev-io/hero.jpg"},
    {id:"schoolbreak-io-guide",gameId:"schoolbreak-io",name:"SchoolBreak.io",title:"SchoolBreak.io Guide: Master Chaos & Discipline",date:"2026-06-22",difficulty:2,readTime:8,url:"https://iogameguide.com/guides/schoolbreak-io-guide",image:"https://iogameguide.com/images/games/schoolbreak-io/hero.jpg"},
    {id:"florr-io-guide",gameId:"florr-io",name:"Florr.io",title:"Florr.io Guide: Master Petals, Crafting & Biome Combat",date:"2026-06-22",difficulty:4,readTime:12,url:"https://iogameguide.com/guides/florr-io-guide",image:"https://iogameguide.com/images/games/florr-io/hero.jpg"},

    {
        id: 'devast-io-guide',
        gameId: 'devast-io',
        name: 'Devast.io',
        title: 'Devast.io Guide: Master Survival, Crafting & Base Building',
        date: '2026-06-24',
        difficulty: 4,
        readTime: 12,
        url: 'https://iogameguide.com/guides/devast-io-guide',
        image: 'https://iogameguide.com/images/games/devast-io/hero.jpg'
    },
    {
        id: 'snake-io-guide',
        title: 'Snake.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Snake.io',
        gameId: 'snake-io',
        date: '2026-06-26',
        url: 'snake-io-guide',
        image: 'snake-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Snake.io is a real-time multiplayer snake battle game that transforms the classic Nokia-era snake game into an intense o...'
    },
    {
        id: 'flyordie-io-guide',
        title: 'FlyOrDie.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'FlyOrDie.io',
        gameId: 'flyordie-io',
        date: '2026-06-26',
        url: 'flyordie-io-guide',
        image: 'flyordie-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'FlyOrDie.io, now known as EvoWorld.io, is a browser‑based multiplayer survival game where you begin as a tiny fly and cl...'
    },
    {
        id: 'limax-io-guide',
        title: 'Limax.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Limax.io',
        gameId: 'limax-io',
        date: '2026-06-26',
        url: 'limax-io-guide',
        image: 'limax-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Limax.io is a multiplayer arena game where players control glowing neon worm‑like snakes in a constantly moving battlefi...'
    },
    {
        id: 'a-slithery-snake-and-snowball-io-guide',
        title: 'A Slithery Snake and Snowball.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'A Slithery Snake and Snowball.io',
        gameId: 'a-slithery-snake-and-snowball-io',
        date: '2026-06-26',
        url: 'a-slithery-snake-and-snowball-io-guide',
        image: 'a-slithery-snake-and-snowball-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'A Slithery Snake and Snowball.io is a winter-themed multiplayer arena game where you control a colorful snake sliding ac...'
    },
    {
        id: 'aipaperanimals-io-guide',
        title: 'AIPaperAnimals.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'AIPaperAnimals.io',
        gameId: 'aipaperanimals-io',
        date: '2026-06-26',
        url: 'aipaperanimals-io-guide',
        image: 'aipaperanimals-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'AIPaperAnimals.io is a competitive multiplayer arena game where players control adorable AI-powered paper animals in a v...'
    },
    {
        id: 'arras-io-guide',
        title: 'Arras.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Arras.io',
        gameId: 'arras-io',
        date: '2026-06-26',
        url: 'arras-io-guide',
        image: 'arras-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Arras.io is a top‑down, multiplayer tank arena game that pits you against other players and AI‑controlled polygons. Deve...'
    },
    {
        id: 'amogus-io-guide',
        title: 'Amogus.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Amogus.io',
        gameId: 'amogus-io',
        date: '2026-06-26',
        url: 'amogus-io-guide',
        image: 'amogus-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Amogus.io is a browser‑based multiplayer arena that fuses the social deduction chaos of Among Us with the territory‑capt...'
    },
    {
        id: 'agma-io-guide',
        title: 'Agma.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Agma.io',
        gameId: 'agma-io',
        date: '2026-06-26',
        url: 'agma-io-guide',
        image: 'agma-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Agma.io is a browser‑based multiplayer arena where players control microscopic cells or organisms in a constantly evolvi...'
    },
    {
        id: 'aquapark-io-guide',
        title: 'AquaPark.io Guide: Tips, Strategies & How to Win Every Race',
        game: 'AquaPark.io',
        gameId: 'aquapark-io',
        date: '2026-06-27',
        url: 'aquapark-io',
        image: 'aquapark-io',
        readTime: '6 min',
        excerpt: 'Master AquaPark.io with shortcut jumps, bumping tactics, power-up strategies, and race-winning tips.'
    }
,
    {
        id: 'arena-io-guide',
        title: 'Arena.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Arena.io',
        gameId: 'arena-io',
        date: '2026-06-28',
        url: 'arena-io-guide',
        image: 'arena-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Arena.io is a fast-paced multiplayer online arena game where players battle against each other in intense combat scenari...'
    },
    {
        id: 'brutal-io-guide',
        title: 'Brutal.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Brutal.io',
        gameId: 'brutal-io',
        date: '2026-06-29',
        url: 'brutal-io-guide',
        image: 'brutal-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Brutal.io is a fast‑paced, physics‑driven arena brawler where players pilot neon‑lit cars and swing massive spiked flail...'
    },
    {
        id: 'battledudes-io-guide',
        title: 'BattleDudes.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BattleDudes.io',
        gameId: 'battledudes-io',
        date: '2026-06-30',
        url: 'battledudes-io-guide',
        image: 'battledudes-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'BattleDudes.io is an action-packed 2D multiplayer .io battle game where chaos and strategy collide on the battlefield. R...'
    },

    
    {
        id: 'archers-io-guide',
        title: 'Archers.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Archers.io',
        gameId: 'archers-io',
        date: '2026-07-01',
        url: 'archers-io-guide',
        image: 'archers-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Archers.io is a fast‑paced multiplayer arena game where you control a lone archer and gradually build an entire army of ...'
    },
    {
        id: 'basketball-io-guide',
        title: 'Basketball.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Basketball.io',
        gameId: 'basketball-io',
        date: '2026-07-02',
        url: 'basketball-io-guide',
        image: 'basketball-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Basketball.io is a free, browser‑based multiplayer basketball arena where you jump into quick 3‑on‑3 matches, pick a cus...'
    },
    {
        id: 'boxer-io-guide',
        title: 'Boxer.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Boxer.io',
        gameId: 'boxer-io',
        date: '2026-07-03',
        url: 'boxer-io-guide',
        image: 'boxer-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Boxer.io is a fast‑paced multiplayer boxing game where stick‑style fighters clash in a vibrant arena. Unlike traditional...'
    },
    {
        id: 'axes-io-guide',
        title: 'AXES.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'AXES.io',
        gameId: 'axes-io',
        date: '2026-07-04',
        url: 'axes-io-guide',
        image: 'axes-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'AXES.io is a fast-paced mobile battle royale where players compete in arena combat by throwing axes at opponents to beco...'
    },
    {
        id: 'axe-io-guide',
        title: 'Axe.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Axe.io',
        gameId: 'axe-io',
        date: '2026-07-05',
        url: 'axe-io-guide',
        image: 'axe-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Axe.io is a fast‑paced multiplayer .io arena where each player wields a single throwing axe and battles to dominate the ...'
    },
    {
        id: 'bighole-io-guide',
        title: 'BigHole.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BigHole.io',
        gameId: 'bighole-io',
        date: '2026-07-06',
        url: 'bighole-io-guide',
        image: 'bighole-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'BigHole.io is a competitive multiplayer game where you control a growing black hole that devours objects, buildings, and...'
    },
    {
        id: 'bruh-io-guide',
        title: 'Bruh.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Bruh.io',
        gameId: 'bruh-io',
        date: '2026-07-07',
        url: 'bruh-io-guide',
        image: 'bruh-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Bruh.io is a fast‑paced, browser‑based multiplayer battle royale where you drop onto a shrinking arena, scavenge weapons...'
    },
    {
        id: 'brosswordz-io-guide',
        title: 'BrosSwordz.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BrosSwordz.io',
        gameId: 'brosswordz-io',
        date: '2026-07-08',
        url: 'brosswordz-io-guide',
        image: 'brosswordz-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'BrosSwordz.io is a fast‑paced, browser‑based multiplayer sword battle arena where players choose from a roster of swords...'
    },
    {
        id: 'basketbros-io-guide',
        title: 'BasketBros.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BasketBros.io',
        gameId: 'basketbros-io',
        date: '2026-07-09',
        url: 'basketbros-io-guide',
        image: 'basketbros-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'BasketBros.io is a fast-paced, browser-based arcade basketball game developed by Blue Wizard Digital LP that strips away...'
    },
    {
        id: 'buildroyale-io-guide',
        title: 'BuildRoyale.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BuildRoyale.io',
        gameId: 'buildroyale-io',
        date: '2026-07-10',
        url: 'buildroyale-io-guide',
        image: 'buildroyale-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'BuildRoyale.io is a fast-paced, browser-based battle royale game where building and shooting seamlessly blend. Unlike tr...'
    },
    {
        id: 'copter-io-guide',
        title: 'Copter.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Copter.io',
        gameId: 'copter-io',
        date: '2026-07-11',
        url: 'copter-io-guide',
        image: 'copter-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Copter.io is a thrilling multiplayer .io game that drops you into an intense aerial battlefield as the pilot of a custom...'
    },
    {
        id: 'battlepoint-io-guide',
        title: 'Battlepoint.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Battlepoint.io',
        gameId: 'battlepoint-io',
        date: '2026-07-12',
        url: 'battlepoint-io-guide',
        image: 'battlepoint-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Battlepoint.io is a fast-paced, multiplayer top-down shooter that drops you into an explosive, shrinking arena. Unlike t...'
    },
    {
        id: 'braains-io-guide',
        title: 'Braains.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Braains.io',
        gameId: 'braains-io',
        date: '2026-07-13',
        url: 'braains-io-guide',
        image: 'braains-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Braains.io is a thrilling multiplayer zombie survival arena where players choose their destiny: fight for survival as a ...'
    },
    {
        id: 'aquar-io-guide',
        title: 'Aquar.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Aquar.io',
        gameId: 'aquar-io',
        date: '2026-07-14',
        url: 'aquar-io-guide',
        image: 'aquar-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Aquar.io is the highly anticipated sequel to Oceanar.io, offering a fascinating multiplayer underwater ecosystem where y...'
    },
    {
        id: 'babyshark-io-guide',
        title: 'BabyShark.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BabyShark.io',
        gameId: 'babyshark-io',
        date: '2026-07-15',
        url: 'babyshark-io-guide',
        image: 'babyshark-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'BabyShark.io is a vibrant, browser-based multiplayer survival game that puts a playful twist on the classic eat-and-grow...'
    },
    {
        id: 'bombom-io-guide',
        title: 'BomBom.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BomBom.io',
        gameId: 'bombom-io',
        date: '2026-07-16',
        url: 'bombom-io-guide',
        image: 'bombom-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'BomBom.io is a fast-paced, explosive multiplayer arena game that puts a thrilling spin on the classic bomberman formula....'
    },
    {
        id: 'block-io-guide',
        title: 'Block.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Block.io',
        gameId: 'block-io',
        date: '2026-07-17',
        url: 'block-io-guide',
        image: 'block-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Block.io is a thrilling free-to-play multiplayer browser game that combines the addictive nature of classic IO titles wi...'
    },
    {
        id: 'animal-io-guide',
        title: 'Animal.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Animal.io',
        gameId: 'animal-io',
        date: '2026-07-18',
        url: 'animal-io-guide',
        image: 'animal-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Animal.io is a chaotic multiplayer arena game where players evolve their animals by consuming food and knocking opponent...'
    },
    {
        id: 'battle-io-guide',
        title: 'Battle.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Battle.io',
        gameId: 'battle-io',
        date: '2026-07-19',
        url: 'battle-io-guide',
        image: 'battle-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Battle.io is a thrilling, fast-paced multiplayer battle arena that drops you into a chaotic top-down battlefield where o...'
    },
    {
        id: 'zombs-royale-io-guide',
        title: 'ZombsRoyale.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'ZombsRoyale.io',
        gameId: 'zombs-royale-io',
        date: '2026-07-20',
        url: 'zombs-royale-io-guide',
        image: 'zombs-royale-io',
        difficulty: 4,
        readTime: '8 min',
        excerpt: 'ZombsRoyale.io is a fast-paced 2D top-down battle royale dropping 100 players onto an island. Loot weapons, survive the gas...'
    },
    {
        id: 'battletabs-io-guide',
        title: 'BattleTabs.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BattleTabs.io',
        gameId: 'battletabs-io',
        date: '2026-07-21',
        url: 'battletabs-io-guide',
        image: 'battletabs-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'BattleTabs.io reimagines classic Battleship as a fast, asynchronous PvP naval combat game. Instead of waiting for oppone...'
    },
    {
        id: 'bloxdhop-io-guide',
        title: 'BloxdHop.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BloxdHop.io',
        gameId: 'bloxdhop-io',
        date: '2026-07-22',
        url: 'bloxdhop-io-guide',
        image: 'bloxdhop-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'BloxdHop.io is a captivating, Minecraft-inspired multiplayer parkour game that challenges players to navigate treacherou...'
    },
    {
        id: 'brainrots-io-guide',
        title: 'Brainrots.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Brainrots.io',
        gameId: 'brainrots-io',
        date: '2026-07-23',
        url: 'brainrots-io-guide',
        image: 'brainrots-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Brainrots.io is a chaotic multiplayer arena game that blends classic .io snake mechanics with the absurd, viral humor of...'
    },
    {
        id: 'battleboats-io-guide',
        title: 'Battleboats.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Battleboats.io',
        gameId: 'battleboats-io',
        date: '2026-07-24',
        url: 'battleboats-io-guide',
        image: 'battleboats-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Battleboats.io is a thrilling real-time multiplayer naval strategy game that reinvents the classic Battleship experience...'
    },
    {
        id: 'adventuremoomoo-io-guide',
        title: 'AdventureMoomoo.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'AdventureMoomoo.io',
        gameId: 'adventuremoomoo-io',
        date: '2026-07-25',
        url: 'adventuremoomoo-io-guide',
        image: 'adventuremoomoo-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'AdventureMoomoo.io is a thrilling multiplayer animal sandbox survival game where players gather resources, craft powerfu...'
    },
    {
        id: 'badegg-io-guide',
        title: 'Badegg.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Badegg.io',
        gameId: 'badegg-io',
        date: '2026-07-26',
        url: 'badegg-io-guide',
        image: 'badegg-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Badegg.io is a chaotic, physics-based multiplayer arena game where your ultimate goal is to be the last egg standing. Un...'
    },
    {
        id: 'battles-io-guide',
        title: 'Battles.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Battles.io',
        gameId: 'battles-io',
        date: '2026-07-27',
        url: 'battles-io-guide',
        image: 'battles-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Battles.io is a fast-paced, browser-based multiplayer strategy game where quick thinking meets fierce competition. Unlik...'
    },
    {
        id: 'battlefields-io-guide',
        title: 'Battlefields.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Battlefields.io',
        gameId: 'battlefields-io',
        date: '2026-07-28',
        url: 'battlefields-io-guide',
        image: 'battlefields-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Battlefields.io is a fast-paced, multiplayer browser strategy game where you step into the boots of a battle-hardened lo...'
    },
    {
        id: 'alis-io-guide',
        title: 'Alis.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Alis.io',
        gameId: 'alis-io',
        date: '2026-07-29',
        url: 'alis-io-guide',
        image: 'alis-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Alis.io is a thrilling multiplayer online arena game that combines the classic cell-eating mechanics of Agar.io with fas...'
    },
    {
        id: 'bladers-io-guide',
        title: 'Bladers.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Bladers.io',
        gameId: 'bladers-io',
        date: '2026-07-30',
        url: 'bladers-io-guide',
        image: 'bladers-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Bladers.io is an exhilarating online multiplayer arena game where players control high-speed spinning tops in intense ba...'
    },
    {
        id: 'antwar-io-guide',
        title: 'AntWar.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'AntWar.io',
        gameId: 'antwar-io',
        date: '2026-07-31',
        url: 'antwar-io-guide',
        image: 'antwar-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'AntWar.io is a highly strategic multiplayer browser game where you build, manage, and defend your ant colony while battl...'
    },
    {
        id: 'bopz-io-guide',
        title: 'BOPZ.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BOPZ.io',
        gameId: 'bopz-io',
        date: '2026-08-01',
        url: 'bopz-io-guide',
        image: 'bopz-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'BOPZ.io is a highly competitive, top-down 2D tactical shooter engineered by End Game Interactive, the creators of ZombsR...'
    },
    {
        id: 'battlegrounds-io-guide',
        title: 'Battlegrounds.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Battlegrounds.io',
        gameId: 'battlegrounds-io',
        date: '2026-08-02',
        url: 'battlegrounds-io-guide',
        image: 'battlegrounds-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Battlegrounds.io is a fast-paced, pixel-art multiplayer battle royale that drops you into a shrinking arena where only o...'
    },
    {
        id: 'bighero-io-guide',
        title: 'BigHero.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BigHero.io',
        gameId: 'bighero-io',
        date: '2026-08-03',
        url: 'bighero-io-guide',
        image: 'bighero-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'BigHero.io is a fast-paced multiplayer superhero arena game where players battle to become the ultimate hero. What makes...'
    },
    {
        id: 'airwings-io-guide',
        title: 'AirWings.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'AirWings.io',
        gameId: 'airwings-io',
        date: '2026-08-04',
        url: 'airwings-io-guide',
        image: 'airwings-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'AirWings.io is a thrilling, fast-paced multiplayer aerial combat game that drops you right into the cockpit of a fighter...'
    },
    {
        id: 'bombhopper-io-guide',
        title: 'BombHopper.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BombHopper.io',
        gameId: 'bombhopper-io',
        date: '2026-08-05',
        url: 'bombhopper-io-guide',
        image: 'bombhopper-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'BombHopper.io is a brilliant physics-based platformer that completely reimagines movement. Developed by Julien Mourer, t...'
    },
    {
        id: 'armedforces-io-guide',
        title: 'ArmedForces.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'ArmedForces.io',
        gameId: 'armedforces-io',
        date: '2026-08-06',
        url: 'armedforces-io-guide',
        image: 'armedforces-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'ArmedForces.io is a fast-paced, browser-based military first-person shooter that drops you directly into intense, team-b...'
    },
    {
        id: 'beetles-io-guide',
        title: 'Beetles.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Beetles.io',
        gameId: 'beetles-io',
        date: '2026-08-06',
        url: 'beetles-io-guide',
        image: 'beetles-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Beetles.io is a fast-paced multiplayer survival arena where you control a baby beetle, eat to grow, and battle other ins...'
    },
    {
        id: 'carfight-io-guide',
        title: 'CarFight.io: 5 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'CarFight.io',
        gameId: 'carfight-io',
        date: '2026-08-06',
        url: 'carfight-io-guide',
        image: 'carfight-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'You keep plummeting off the roof. I see you out there, driving straight into the center of a 2v1 and wondering why your ...'
    },
    {
        id: 'bist-io-guide',
        title: 'Bist.io: 6 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'Bist.io',
        gameId: 'bist-io',
        date: '2026-08-07',
        url: 'bist-io-guide',
        image: 'bist-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'You keep dying in the first five minutes. You spawn, run blindly into the desert, get roasted by a tier 3 predator, and ...'
    },
    {
        id: 'cavegame-io-guide',
        title: 'Cavegame.io: 6 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'Cavegame.io',
        gameId: 'cavegame-io',
        date: '2026-08-08',
        url: 'cavegame-io-guide',
        image: 'cavegame-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'You keep dying in the caves. You spawn, you mine, you get jumped by a guy with diamond gear, and you lose everything. St...'
    },
    {
        id: 'bubbleman-io-guide',
        title: 'Bubbleman.io: Every Play Style Ranking Ranked — Which One Actually Wins?',
        game: 'Bubbleman.io',
        gameId: 'bubbleman-io',
        date: '2026-08-09',
        url: 'bubbleman-io-guide',
        image: 'bubbleman-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'What is up, .io fans! Everyone in the Bubbleman.io community is arguing about the best way to dominate those chaotic 30-...'
    },
    {
        id: 'anguis-io-guide',
        title: 'Anguis.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Anguis.io',
        gameId: 'anguis-io',
        date: '2026-08-10',
        url: 'anguis-io-guide',
        image: 'anguis-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Anguis.io is a highly competitive multiplayer snake game that challenges you to slither your way to supremacy in a vibra...'
    },
    {
        id: 'astrodud-io-guide',
        title: 'Astrodud.io: 5 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'Astrodud.io',
        gameId: 'astrodud-io',
        date: '2026-08-11',
        url: 'astrodud-io-guide',
        image: 'astrodud-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'You keep dying in the first thirty seconds. I see you. You spawn in, panic, and immediately faceplant into a pit trap or...'
    },
    {
        id: 'cellcraft-io-guide',
        title: 'Cellcraft.io: 5 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'Cellcraft.io',
        gameId: 'cellcraft-io',
        date: '2026-08-11',
        url: 'cellcraft-io-guide',
        image: 'cellcraft-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'You keep dying in the first five minutes, don\'t you? You spawn, you eat a few pellets, and then some veteran turns you i...'
    },
    {
        id: 'candy-io-guide',
        title: 'Candy.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Candy.io',
        gameId: 'candy-io',
        date: '2026-08-12',
        url: 'candy-io-guide',
        image: 'candy-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Candy.io is a vibrant, slithering survival game set in a colorful candy-themed world. Unlike standard io games, it immer...'
    },
    {
        id: 'bball-io-guide',
        title: 'BBall.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'BBall.io',
        gameId: 'bball-io',
        date: '2026-08-13',
        url: 'bball-io-guide',
        image: 'bball-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'BBall.io is a fast-paced, 3D multiplayer basketball game that brings the thrill of the court directly to your browser. U...'
    },
    {
        id: 'basketballmoomoo-io-guide',
        title: 'BasketballMoomoo.io: 5 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'BasketballMoomoo.io',
        gameId: 'basketballmoomoo-io',
        date: '2026-08-14',
        url: 'basketballmoomoo-io-guide',
        image: 'basketballmoomoo-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'You keep getting robbed blind and watching your score flatline because you play like a total casual. I have over two tho...'
    },
    {
    id: 'castlesiege-io',
    name: 'Castlesiege.io',
    icon: '🏰',
    iconColor: '#f59e0b',
    guideCount: 1,
    difficulty: 3,
    tags: ["multiplayer", "strategy", "action"],
    description: 'Play Castlesiege.io online - a multiplayer browser strategy game.'
    },
    {
        id: 'castlesiege-io-guide',
        title: 'Castlesiege.io: Every Upgrade Build Strategies Ranked — Which One Actually Wins?',
        game: 'Castlesiege.io',
        gameId: 'castlesiege-io',
        date: '2026-08-16',
        url: 'castlesiege-io-guide',
        image: 'castlesiege-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Everyone in the Castlesiege.io community argues about the best way to spend your hard-earned upgrade points. Some say yo...'
    },
    {
    id: 'chompers-io',
    name: 'Chompers.io',
    icon: '🦖',
    iconColor: '#FFC107',
    guideCount: 1,
    difficulty: 2,
    tags: ["io", "battle", "strategy"],
    description: 'Lead a magical creature to eat treats, fight other players with various weapons, and grow to become the largest in a competitive multiplayer arena.'
    },
    {
        id: 'chompers-io-guide',
        title: 'Chompers.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Chompers.io',
        gameId: 'chompers-io',
        date: '2026-08-17',
        url: 'chompers-io-guide',
        image: 'chompers-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Chompers.io is an intense, evolution-based multiplayer arena game where you control a magical creature competing to beco...'
    },
    {
    id: 'colonist-io',
    name: 'Colonist.io',
    icon: '🏝️',
    iconColor: '#4CAF50',
    guideCount: 1,
    difficulty: 3,
    tags: ["Board Game", "Strategy", "Multiplayer"],
    description: 'Inspired by Catan, this online board game has players collect resources, trade, and build settlements and cities on a hexagonal map to be the first to reach 10 victory points.'
    },
    {
        id: 'colonist-io-guide',
        title: 'Colonist.io: 6 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'Colonist.io',
        gameId: 'colonist-io',
        date: '2026-08-18',
        url: 'colonist-io-guide',
        image: 'colonist-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'You keep losing because you play like a tourist. I have over two thousand hours in Colonist.io. I have watched you throw...'
    },
    {
    id: 'catac-io',
    name: 'Catac.io',
    icon: '🐱',
    iconColor: '#FF4B4B',
    guideCount: 1,
    difficulty: 2,
    tags: ["IO", "Action", "Multiplayer"],
    description: 'Battle as an astronaut cat in a space arena, using melee weapons to eliminate others, collect coins, and upgrade your gear in this fast-paced multiplayer survival game.'
    },
    {
        id: 'catac-io-guide',
        title: 'Catac.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Catac.io',
        gameId: 'catac-io',
        date: '2026-08-19',
        url: 'catac-io-guide',
        image: 'catac-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Catac.io is a fast-paced multiplayer .io action game where you battle as an astronaut cat in a space arena. Inspired by ...'
    },
    {
    id: 'browser-minecraft-clone-io',
    name: 'Mine-Craft.io',
    icon: '⛏️',
    iconColor: '#7CB342',
    guideCount: 1,
    difficulty: 2,
    tags: ["Sandbox", "Crafting", "Multiplayer"],
    description: 'Mine-Craft.io is a free-to-play multiplayer browser game that brings a Minecraft-like building and crafting experience directly to your web browser.'
    },
    {
        id: 'browser-minecraft-clone-io-guide',
        title: 'Mine-Craft.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Mine-Craft.io',
        gameId: 'browser-minecraft-clone-io',
        date: '2026-08-20',
        url: 'browser-minecraft-clone-io-guide',
        image: 'browser-minecraft-clone-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'Mine-Craft.io is a free-to-play multiplayer browser game that delivers a comprehensive Minecraft-like building and craft...'
    },
    {
    id: 'arenapoxel-io',
    name: 'Poxel.io',
    icon: '🔫',
    iconColor: '#FF5733',
    guideCount: 1,
    difficulty: 4,
    tags: ["FPS", "Shooter", "Multiplayer"],
    description: 'Poxel.io is a fast-paced, skill-driven 3D voxel first-person shooter featuring intense arena combat with modes like Free-For-All, Team Deathmatch, and Domination.'
    },
    {
        id: 'arenapoxel-io-guide',
        title: 'Poxel.io: 5 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'Poxel.io',
        gameId: 'arenapoxel-io',
        date: '2026-08-21',
        url: 'arenapoxel-io-guide',
        image: 'arenapoxel-io',
        difficulty: 4,
        readTime: '8 min',
        excerpt: 'You keep spawning, dying, and staring at the leaderboard at the bottom. It is embarrassing. I have over 2000 hours in Po...'
    },
    {
    id: 'cryzen-io',
    name: 'Cryzen.io',
    icon: '🔫',
    iconColor: '#FF4500',
    guideCount: 1,
    difficulty: 3,
    tags: ["FPS", "Shooter", "Multiplayer"],
    description: 'A fast-paced multiplayer first-person shooter where players engage in Deathmatch and Team Deathmatch battles using precise aiming and tactical movement to survive and dominate the arena.'
    },
    {
        id: 'cryzen-io-guide',
        title: 'Cryzen.io: 5 Fatal Mistakes Killing Your Runs (And How to Fix Them)',
        game: 'Cryzen.io',
        gameId: 'cryzen-io',
        date: '2026-08-22',
        url: 'cryzen-io-guide',
        image: 'cryzen-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'You keep dying in the spawn hallway. Again. I have over 2000 hours in Cryzen.io, and I watch new players make the exact ...'
    },
    {
    id: 'browser-minecraft-modes-io',
    name: 'Vectaria.io',
    icon: '⛏️',
    iconColor: '#5D9E5A',
    guideCount: 1,
    difficulty: 2,
    tags: ["Action", "Adventure", "Multiplayer"],
    description: 'A 3D multiplayer .io game where players mine resources, craft items, build structures, and fight others across Survival, Creative, and PvP modes.'
    },
    {
        id: 'browser-minecraft-modes-io-guide',
        title: 'Vectaria.io: Every Vectaria Play Styles Ranked — Which One Actually Wins?',
        game: 'Vectaria.io',
        gameId: 'browser-minecraft-modes-io',
        date: '2026-08-23',
        url: 'browser-minecraft-modes-io-guide',
        image: 'browser-minecraft-modes-io',
        difficulty: 2,
        readTime: '8 min',
        excerpt: 'What’s up, guys! Today we’re diving deep into Vectaria.io. Everyone argues about the \'best\' way to play this game. Do yo...'
    },
    {
    id: 'craftnite-io',
    name: 'Craftnite.io',
    icon: '🧱',
    iconColor: '#4CAF50',
    guideCount: 1,
    difficulty: 3,
    tags: ["FPS", "Battle Royale", "Crafting"],
    description: 'A browser-based FPS battle royale where players gather resources, craft weapons, and build structures to survive a shrinking map and defeat opponents.'
    },
    {
        id: 'craftnite-io-guide',
        title: 'Craftnite.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Craftnite.io',
        gameId: 'craftnite-io',
        date: '2026-08-24',
        url: 'craftnite-io-guide',
        image: 'craftnite-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Craftnite.io is an exciting browser-based FPS battle royale that combines fast-paced shooting with deep survival and bui...'
    },
    {
    id: 'arcadestarblast-io',
    name: 'Starblast.io',
    icon: '🚀',
    iconColor: '#0F172A',
    guideCount: 1,
    difficulty: 3,
    tags: ["io", "space", "shooter"],
    description: 'Mine asteroids to collect gems, upgrade your spaceship\'s abilities, and battle other players in a multiplayer space arena.'
    },
    {
        id: 'arcadestarblast-io-guide',
        title: 'Starblast.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'Starblast.io',
        gameId: 'arcadestarblast-io',
        date: '2026-08-26',
        url: 'arcadestarblast-io-guide',
        image: 'arcadestarblast-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'Starblast.io is a high-octane multiplayer arcade space shooter developed by Neuronality that seamlessly blends survival ...'
    },
    {
    id: 'colorwars-io',
    name: 'ColorWars.io',
    icon: '🎨',
    iconColor: '#FF6B6B',
    guideCount: 1,
    difficulty: 3,
    tags: ["IO", "Strategy", "Multiplayer"],
    description: 'Players control a colorful tank to shoot pixel trails and capture territory in a Paper.io-style arena, while managing a gold economy to deploy defenses and eliminate rivals by targeting their trails.'
    },
    {
        id: 'colorwars-io-guide',
        title: 'ColorWars.io Guide: Tips, Strategies & Advanced Techniques',
        game: 'ColorWars.io',
        gameId: 'colorwars-io',
        date: '2026-08-27',
        url: 'colorwars-io-guide',
        image: 'colorwars-io',
        difficulty: 3,
        readTime: '8 min',
        excerpt: 'ColorWars.io is a fast-paced, competitive multiplayer territory-control game published by Kepler Yazilim that blends Pap...'
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



// CDN cache bust 2026-07-01 11:04
