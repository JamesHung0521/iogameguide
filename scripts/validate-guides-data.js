#!/usr/bin/env node
/**
 * 攻略数据验证脚本
 * 用法: node scripts/validate-guides-data.js
 * 检查: 1)语法 2)必填字段 3)字段类型 4)重复项 5)gameId匹配
 */

const fs = require('fs');
const path = require('path');

// 读取 main.js
const mainJsPath = path.join(__dirname, '..', 'js', 'main.js');
const content = fs.readFileSync(mainJsPath, 'utf8');

// 提取 gamesData
const gamesMatch = content.match(/const gamesData = (\[[\s\S]*?\n\]);/);
if (!gamesMatch) {
    console.error('❌ 无法提取 gamesData');
    process.exit(1);
}

// 提取 guidesData
const guidesMatch = content.match(/const guidesData = (\[[\s\S]*?\n\]);/);
if (!guidesMatch) {
    console.error('❌ 无法提取 guidesData');
    process.exit(1);
}

const games = eval(gamesMatch[1]);
const guides = eval(guidesMatch[1]);

const errors = [];
const warnings = [];

// 1. 检查 undefined
const undefGames = games.filter(g => g === undefined);
const undefGuides = guides.filter(g => g === undefined);
if (undefGames.length > 0) errors.push(`gamesData 有 ${undefGames.length} 个 undefined 条目`);
if (undefGuides.length > 0) errors.push(`guidesData 有 ${undefGuides.length} 个 undefined 条目`);

// 过滤掉 undefined
const validGames = games.filter(g => g);
const validGuides = guides.filter(g => g);

// 2. 检查 gamesData 必填字段
const requiredGameFields = ['id', 'name', 'icon', 'iconColor', 'guideCount', 'difficulty', 'tags', 'description'];
validGames.forEach((game, i) => {
    requiredGameFields.forEach(field => {
        if (game[field] === undefined || game[field] === null || game[field] === '') {
            errors.push(`gamesData[${i}] (${game.name || game.id || 'unknown'}) 缺少字段: ${field}`);
        }
    });
});

// 3. 检查 guidesData 必填字段（统一格式）
const requiredGuideFields = ['id', 'title', 'gameId', 'date'];
const optionalGuideFields = ['name', 'game', 'readTime', 'excerpt', 'difficulty', 'category', 'tags', 'url', 'image'];

validGuides.forEach((guide, i) => {
    // 检查 id 或 slug（兼容旧格式）
    if (!guide.id && !guide.slug) {
        errors.push(`guidesData[${i}] 缺少 id 或 slug`);
    }
    
    // 检查必填字段
    requiredGuideFields.forEach(field => {
        if (guide[field] === undefined || guide[field] === null || guide[field] === '') {
            errors.push(`guidesData[${i}] (${guide.id || guide.slug || guide.name || 'unknown'}) 缺少字段: ${field}`);
        }
    });
    
    // 检查字段类型一致性
    if (guide.difficulty !== undefined) {
        if (typeof guide.difficulty === 'string') {
            warnings.push(`guidesData[${i}] difficulty 是字符串 "${guide.difficulty}"，建议改为数字 1-5`);
        } else if (typeof guide.difficulty === 'number' && (guide.difficulty < 1 || guide.difficulty > 5)) {
            errors.push(`guidesData[${i}] difficulty ${guide.difficulty} 不在 1-5 范围内`);
        }
    }
    
    if (guide.readTime !== undefined) {
        if (typeof guide.readTime === 'string' && !guide.readTime.match(/^\d+ min$/)) {
            warnings.push(`guidesData[${i}] readTime "${guide.readTime}" 格式不标准，建议改为数字`);
        }
    }
});

// 4. 检查重复项
const gameIdSet = new Set();
validGames.forEach((game, i) => {
    if (gameIdSet.has(game.id)) {
        errors.push(`gamesData 有重复 id: ${game.id}`);
    }
    gameIdSet.add(game.id);
});

const guideIdSet = new Set();
validGuides.forEach((guide, i) => {
    const id = guide.id || guide.slug;
    if (guideIdSet.has(id)) {
        errors.push(`guidesData 有重复 id: ${id}`);
    }
    guideIdSet.add(id);
});

// 5. 检查 gameId 匹配
const gameIdSet2 = new Set(validGames.map(g => g.id));
validGuides.forEach((guide, i) => {
    if (guide.gameId && !gameIdSet2.has(guide.gameId)) {
        errors.push(`guidesData[${i}] (${guide.id || guide.slug}) gameId "${guide.gameId}" 在 gamesData 中不存在`);
    }
});

// 输出结果
console.log(`\n📊 数据统计:`);
console.log(`   游戏: ${validGames.length} 个`);
console.log(`   攻略: ${validGuides.length} 篇`);

if (errors.length === 0 && warnings.length === 0) {
    console.log('\n✅ 数据验证通过！');
    process.exit(0);
} else {
    if (errors.length > 0) {
        console.log(`\n❌ 错误 (${errors.length}):`);
        errors.forEach(e => console.log(`   - ${e}`));
    }
    if (warnings.length > 0) {
        console.log(`\n⚠️  警告 (${warnings.length}):`);
        warnings.forEach(w => console.log(`   - ${w}`));
    }
    process.exit(errors.length > 0 ? 1 : 0);
}
