# 🀄 HK-MON 港精靈 Card Game

**Pokémon 風格 · 香港原創卡牌對戰遊戲 — 一眼就知係香港人整嘅 Game！**
*A Pokémon-style card battle game with Hong Kong flavour — 60 original cards, 4 languages, 8-bit sound effects, 100% free.*

繁體中文（香港）｜ English ｜ 日本語 ｜ 한국어

---

## ✨ 特色 Features

| | |
|---|---|
| 🀄 **60 張原創卡牌** | 48 隻港味精靈（火鍋牛魔王、叮叮俠、紅Van車神、舞火龍、巴士阿叔、絲襪奶茶…）+ 12 件道具 |
| 🈯 **中英日韓四語** | 遊戲內即時切換，卡名／招式／圖鑑全部四語 |
| ⚔️ **完整玩法** | 屬性相剋、會心一擊、燒傷／麻痺、冷卻招式、道具、AI 對手 |
| 🔊 **8-bit 音效** | 純程式合成，攻擊／回血／勝利音效全齊（可靜音） |
| 🏆 **兩種模式** | 單場對戰 + 三連霸（Gauntlet，最終關打「終極港靈王」） |
| 😴🔥 **三種難度** | 街場 Easy ／ 波樓 Normal ／ 決戰獅子山 Hard |
| ♻️ **完全免費** | 冇廣告、冇課金、開源 |

## 🎮 玩法流程 Game Flow

```
揀語言 → 揀玩法（單場／三連霸）→ 揀難度 → 揀隊伍（5 精靈 + 3 道具）
   → 輪流行動：攻擊 / 換精靈 / 用道具
   → 屬性相剋 ×1.5 · 會心 ×1.6 · 招式 2 有冷卻
   → 打低對手全部 5 隻就贏！
```

- **屬性**：🔥火鍋 ＞ 🌿山林 ＞ 🌊港水 ＞ 🔥火鍋；🔮靈界 ＞ ⚡雷電 ＞ 🌊港水；⭐街坊中立
- **狀態**：燒傷每回合扣血；麻痺 35% 郁唔到（持續 2 回合）
- **突然死亡**：第 50 回合起雙方每回合扣血

## 🚀 本機運行 Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## ☁️ 部署到 Streamlit Community Cloud

1. Push 呢個 repo 去 GitHub（要有 `master` branch 同根目錄 `streamlit_app.py`）
2. 去 [share.streamlit.io](https://share.streamlit.io) → **Deploy an app**
3. Repository: `disneydisney88/CARDGAME`　Branch: `master`　Main file: `streamlit_app.py`
4. 撳 **Deploy** — 搞掂！

## 📁 檔案結構

```
streamlit_app.py    主程式（主頁／組隊／戰鬥／圖鑑／說明）
hkmon_data.py       60 張卡 + 隊伍 + 屬性表（四語）
hkmon_i18n.py       UI 文字（四語）
hkmon_engine.py     戰鬥引擎 + AI
hkmon_sfx.py        8-bit 音效合成 + CCv2 播放器
hkmon_styles.py     卡面 HTML/CSS（TCG 風格）
.streamlit/config.toml   深色霓虹主題
```

## 🙏 credits

- 玩法與卡面排版致敬經典 Pokémon TCG；所有卡牌、名字、文字均為**原創**香港題材內容。
- 本作品為粉絲致敬之作，與 Nintendo / Creatures Inc. / GAME FREAK inc. / The Pokémon Company 無關。
- 参考/靈感：open-source 卡牌遊戲社群（pokemontcg 卡面排版、各種 open-source turn-based battle engine）。

License: MIT — 隨便玩、隨便改，記得請我飲杯絲襪奶茶 🧋
