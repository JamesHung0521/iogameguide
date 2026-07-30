// Firebase Configuration for iogameguide.com
// Using compat SDK for static site compatibility

const firebaseConfig = {
  apiKey: "AIzaSyDgV-WHkqH6pjnz1zIe-Cc651wWBs6dnys",
  authDomain: "iogameguide.firebaseapp.com",
  databaseURL: "https://iogameguide-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "iogameguide",
  storageBucket: "iogameguide.firebasestorage.app",
  messagingSenderId: "997718057852",
  appId: "1:997718057852:web:64ce273e0f5d5c969ebaf9",
  measurementId: "G-7QWN66G1WB"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const tierListDB = firebase.database();
const tierListAuth = firebase.auth();

// Sign in anonymously
tierListAuth.signInAnonymously().catch(err => {
  console.warn('Firebase auth failed, tier list will use local mode:', err);
});

// Tier List Module
const TierList = {
  // Tier definitions
  tiers: [
    { letter: 'S', score: 5, color: '#ff4444', label: 'S Tier' },
    { letter: 'A', score: 4, color: '#ff8800', label: 'A Tier' },
    { letter: 'B', score: 3, color: '#ffbb33', label: 'B Tier' },
    { letter: 'C', score: 2, color: '#00b894', label: 'C Tier' },
    { letter: 'D', score: 1, color: '#74b9ff', label: 'D Tier' }
  ],

  // Get anonymous user ID (stored in localStorage for dedup)
  getUserId: function() {
    let uid = localStorage.getItem('tierlist_uid');
    if (!uid) {
      uid = 'anon_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('tierlist_uid', uid);
    }
    return uid;
  },

  // Check if user has already voted for a game
  hasVoted: function(gameId) {
    const votes = JSON.parse(localStorage.getItem('tierlist_votes') || '{}');
    return votes[gameId] !== undefined;
  },

  // Get user's previous vote for a game
  getUserVote: function(gameId) {
    const votes = JSON.parse(localStorage.getItem('tierlist_votes') || '{}');
    return votes[gameId] || null;
  },

  // Submit a vote
  submitVote: function(gameId, tierLetter) {
    const uid = this.getUserId();
    const score = this.tiers.find(t => t.letter === tierLetter).score;

    // Save to localStorage
    const votes = JSON.parse(localStorage.getItem('tierlist_votes') || '{}');
    const previousVote = votes[gameId];
    votes[gameId] = tierLetter;
    localStorage.setItem('tierlist_votes', JSON.stringify(votes));

    // Write to Firebase
    const voteRef = tierListDB.ref('votes/' + gameId + '/' + uid);
    voteRef.set({
      tier: tierLetter,
      score: score,
      timestamp: Date.now()
    });

    return { tierLetter, previousVote };
  },

  // Listen to vote data for a game and return aggregate
  listenToGameVotes: function(gameId, callback) {
    const ref = tierListDB.ref('votes/' + gameId);
    ref.on('value', (snapshot) => {
      const data = snapshot.val();
      if (!data) {
        callback({ avgScore: 0, totalVotes: 0, tier: null });
        return;
      }
      const votes = Object.values(data);
      const totalVotes = votes.length;
      const totalScore = votes.reduce((sum, v) => sum + v.score, 0);
      const avgScore = totalVotes > 0 ? totalScore / totalVotes : 0;
      const tier = this.scoreToTier(avgScore);
      callback({ avgScore, totalVotes, tier });
    });
  },

  // Convert score to tier letter
  scoreToTier: function(score) {
    if (score >= 4.5) return 'S';
    if (score >= 3.5) return 'A';
    if (score >= 2.5) return 'B';
    if (score >= 1.5) return 'C';
    return 'D';
  },

  // Get tier color
  getTierColor: function(letter) {
    const tier = this.tiers.find(t => t.letter === letter);
    return tier ? tier.color : '#999';
  },

  // Get all games vote data once (for Top 10)
  getAllGamesRanking: function(callback) {
    tierListDB.ref('votes').once('value').then((snapshot) => {
      const allData = snapshot.val();
      const rankings = [];

      if (window.iogameguide && window.iogameguide.games) {
        window.iogameguide.games.forEach(game => {
          const gameVotes = allData && allData[game.id] ? Object.values(allData[game.id]) : [];
          const totalVotes = gameVotes.length;
          const totalScore = gameVotes.reduce((sum, v) => sum + v.score, 0);
          const avgScore = totalVotes > 0 ? totalScore / totalVotes : 0;
          
          // Default score based on difficulty (inverted: easier = higher default)
          const defaultScore = 6 - (game.difficulty || 3);
          const finalScore = totalVotes > 0 ? avgScore : defaultScore * 0.6; // Lower weight for defaults
          
          rankings.push({
            id: game.id,
            name: game.name,
            icon: game.icon,
            iconColor: game.iconColor,
            avgScore: finalScore,
            totalVotes: totalVotes,
            tier: this.scoreToTier(finalScore)
          });
        });
      }

      // Sort by score descending
      rankings.sort((a, b) => b.avgScore - a.avgScore);
      callback(rankings);
    }).catch(err => {
      console.warn('Failed to load rankings, using defaults:', err);
      // Fallback: use difficulty-based defaults
      const rankings = [];
      if (window.iogameguide && window.iogameguide.games) {
        window.iogameguide.games.forEach(game => {
          rankings.push({
            id: game.id,
            name: game.name,
            icon: game.icon,
            iconColor: game.iconColor,
            avgScore: 6 - (game.difficulty || 3),
            totalVotes: 0,
            tier: this.scoreToTier(6 - (game.difficulty || 3))
          });
        });
      }
      rankings.sort((a, b) => b.avgScore - a.avgScore);
      callback(rankings);
    });
  },

  // Render Top 10 widget
  renderTop10: function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    this.getAllGamesRanking((rankings) => {
      const top10 = rankings.slice(0, 10);
      container.innerHTML = top10.map((game, index) => {
        const rank = index + 1;
        const tierColor = this.getTierColor(game.tier);
        const voteText = game.totalVotes > 0 ? `${game.totalVotes} votes` : 'No votes yet';
        const guideLink = `guides/${game.id}-guide`;
        
        return `
          <div class="tierlist-item" data-game-id="${game.id}">
            <span class="tierlist-rank">#${rank}</span>
            <span class="tierlist-icon" style="background:${game.iconColor}">${game.icon || '🎮'}</span>
            <a href="${guideLink}" class="tierlist-name">${game.name}</a>
            <span class="tierlist-badge" style="background:${tierColor}">${game.tier}</span>
          </div>
        `;
      }).join('');
    });
  },

  // Render voting modal
  renderVoteModal: function(containerId) {
    const container = document.getElementById(containerId);
    if (!container || !window.iogameguide || !window.iogameguide.games) return;

    const games = window.iogameguide.games;
    const pageSize = 10;
    let currentPage = 0;

    const renderPage = () => {
      const start = currentPage * pageSize;
      const pageGames = games.slice(start, start + pageSize);
      const totalPages = Math.ceil(games.length / pageSize);

      container.innerHTML = `
        <div class="vote-modal-content">
          <div class="vote-modal-header">
            <h3>⚖️ Rate .io Games</h3>
            <button class="vote-modal-close" onclick="TierList.closeVoteModal()">&times;</button>
          </div>
          <div class="vote-modal-body">
            ${pageGames.map(game => {
              const userVote = this.getUserVote(game.id);
              return `
                <div class="vote-game-row">
                  <span class="vote-game-icon" style="background:${game.iconColor}">${game.icon || '🎮'}</span>
                  <span class="vote-game-name">${game.name}</span>
                  <div class="vote-buttons" data-game-id="${game.id}">
                    ${this.tiers.map(t => `
                      <button class="vote-btn ${userVote === t.letter ? 'voted' : ''}" 
                              style="${userVote === t.letter ? 'background:' + t.color : ''}"
                              onclick="TierList.castVote('${game.id}', '${t.letter}')">${t.letter}</button>
                    `).join('')}
                  </div>
                </div>
              `;
            }).join('')}
          </div>
          <div class="vote-modal-footer">
            <button class="vote-nav-btn" onclick="TierList.prevPage()" ${currentPage === 0 ? 'disabled' : ''}>← Prev</button>
            <span class="vote-page-info">Page ${currentPage + 1} / ${totalPages}</span>
            <button class="vote-nav-btn" onclick="TierList.nextPage()" ${currentPage >= totalPages - 1 ? 'disabled' : ''}>Next →</button>
          </div>
        </div>
      `;
    };

    this._renderVotePage = renderPage;
    this._totalPages = Math.ceil(games.length / pageSize);
    renderPage();
  },

  // Cast a vote from modal
  castVote: function(gameId, tierLetter) {
    this.submitVote(gameId, tierLetter);
    // Re-render current page to update button states
    if (this._renderVotePage) this._renderVotePage();
    // Refresh Top 10
    this.renderTop10('tierListTop10');
  },

  // Modal navigation
  prevPage: function() {
    if (currentPage > 0 && this._renderVotePage) {
      currentPage--;
      this._renderVotePage();
    }
  },

  nextPage: function() {
    if (this._renderVotePage) {
      const maxPage = Math.ceil((window.iogameguide.games.length) / 10) - 1;
      if (currentPage < maxPage) {
        currentPage++;
        this._renderVotePage();
      }
    }
  },

  // Open vote modal
  openVoteModal: function() {
    const overlay = document.getElementById('voteModalOverlay');
    if (overlay) {
      overlay.style.display = 'flex';
      this.renderVoteModal('voteModalContent');
      currentPage = 0;
      if (this._renderVotePage) this._renderVotePage();
    }
  },

  // Close vote modal
  closeVoteModal: function() {
    const overlay = document.getElementById('voteModalOverlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  }
};

// Make accessible globally
var currentPage = 0;
window.TierList = TierList;
