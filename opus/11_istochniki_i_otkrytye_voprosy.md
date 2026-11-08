# 11. Источники, непроверенное и вопросы к вам

Все страницы открывались **8 ноября 2026 года**, если не указано иное. Тип данных: **текущее** (на дату), **историческое** (за прошлый период), **прогноз или оценка**, **правило** (условия, параметры, закон).

## Рынок и макро

| Данные | Тип | Что входит и что нет | Источник |
|---|---|---|---|
| BTC $75,900, ETH $2,237 | текущее | цена закрытия дня | [exa BTC](https://exa.ai/library/markets/crypto/BTC), [exa ETH](https://exa.ai/library/markets/crypto/ETH) |
| BTC $102,882, ETH $3,433 на 07.11.2025 | историческое | — | [FRED](https://fred.stlouisfed.org/release/tables?eid=206149&rid=441) |
| SOL $89.25 | текущее | — | [CryptoTicker](https://cryptoticker.io/en/solana-staking-yield-vs-price-drop/) |
| POKT $0.0064, GRT $0.0187 | текущее | — | [CoinMarketCap POKT](https://coinmarketcap.com/currencies/pocket-network/), [Investing GRT](https://www.investing.com/crypto/the-graph/grt-usd-historical-data) |
| GNO $111 (Staking Rewards), $136 (CryptoSlate, август) | текущее / историческое | — | [Staking Rewards](https://www.stakingrewards.com/asset/gnosis), [CryptoSlate](https://cryptoslate.com/a-crypto-network-just-voted-to-abandon-its-standalone-blockchain-and-unlock-27-of-its-token-supply/) |
| Ставка ФРС 3.75–4.00%, эффективная 3.88%, 3-мес. T-bill 4.00% (вторичный рынок) | текущее (на 05.11.2026) | — | [Federal Reserve H.15](https://www.federalreserve.gov/releases/h15/) |
| Рынок закладывает ~74% вероятность повышения ставки 09.12.2026 | прогноз (рыночные ожидания) | — | [CREFC](https://www.crefc.org/cre/cre/content/News/Items/Research_and_Data/2026/Economy_the_Fed_and_Rates_11_03_26.aspx) |
| Курс НБУ 45.3206 грн/$ на 09.11.2026; учётная ставка 16.5% | текущее | — | [mdoffice (данные НБУ)](https://www.mdoffice.com.ua/en/0011/aMDOCurr.download), [Главком](https://glavcom.ua/economics/personal-money/kurs-valjut-8-listopada-2026-skilki-koshtujut-dolar-jevro-i-zlotij-1154126.html) |

## Стейкинг и операторы

| Данные | Тип | Что входит и что нет | Источник |
|---|---|---|---|
| ETH: Network APR 2.71% (CL 2.49% + EL 0.22%); 44.36M ETH в стейкинге; очередь входа ~16–17 дней | текущее | средние по сети; комиссии сервисов не вычтены | [rated.network](https://explorer.rated.network/network?network=mainnet&timeWindow=all&rewardsMetric=average&geoDistType=all&hostDistType=all&soloProDist=stake) |
| 7-дневный APR 2.44%; очередь выхода ~1 день, вывод ~7.1 дня | текущее (06.11.2026) | по validatorqueue.com | [CryptoTicker](https://cryptoticker.io/en/ethereum-price-prediction-staking-queue-november-6-2026/) |
| Lido stETH 2.3% APR | текущее | скользящее среднее за 7 дней, после 10% комиссии Lido | [lido.fi](https://lido.fi/), [калькулятор](https://lido.fi/how-lido-works/apr-and-rewards-calculator) |
| Доходности LST (stETH 2.25%, weETH 2.97%, rETH 1.93%, wBETH 2.21% …) | текущее | APY по DefiLlama, после комиссий протоколов | [defirate](https://defirate.com/staking/) |
| Параметры CSM 0x01: залог 2.4/1.3 ETH (ICS 1.5), доля 3.5% (ICS 6% за 16 ключей), MEV-Boost обязателен, адреса Hoodi и mainnet | правило | — | [operator portal](https://operatorportal.lido.fi/modules/community-staking-module), [блог Lido ICS](https://blog.lido.fi/unlock-exclusive-benefits-as-an-identified-community-staker/), [research.lido.fi](https://research.lido.fi/t/community-staking-module/5917/106) |
| 449 permissionless-операторов, доля 8.04% | текущее | — | [lido.fi/csm](https://lido.fi/csm) |
| Очередь CSM 0 ключей (06.11.2026) | текущее | — | [Dune](https://dune.com/lido/lido-csm) |
| 0x02 CSM: залог 32/30 ETH, доля 2%, старт 23.10.2026 | правило | — | [блог Lido](https://blog.lido.fi/introducing-0x02-csm-a-permissionless-path-to-running-higher-balance-validators/), [research.lido.fi](https://research.lido.fi/t/0x02-csm-landscape/11697) |
| Rocket Pool Saturn 1: залог 4 ETH, 5% + 9% voter share | правило (с 18.02.2026) | — | [docs.rocketpool.net](https://docs.rocketpool.net/upgrades/saturn-1/whats-new.html) |
| Очередь мегапулов: 460 стандартная, 205 экспресс | текущее (06.11.2026) | время ожидания — для уже вышедших из очереди, не прогноз | [RocketDash](https://rocketdash.net/queue) |
| Gnosis: переход в EEZ весной 2027, набор валидаторов упраздняется | правило / план | точная дата форка не объявлена | [Gnosis docs](https://docs.gnosischain.com/node/rewards-penalties), [CoinScreamer](https://coinscreamer.com/gnosis-chain-eez-ethereum-transition-spring-2027/) |
| Solana: инфляция 3.5666%, 68.14% в стейкинге; Alpenglow и билет 0.8 SOL за эпоху с 21.10.2026 | текущее / правило | ставка без MEV | [CryptoTicker](https://cryptoticker.io/en/solana-staking-yield-vs-price-drop/), [solana.com](https://solana.com/upgrades/bls-pubkey-vat), [Solana Compass](https://solanacompass.com/staking/how-much-do-solana-validators-make) |
| Polkadot: ~2.76–2.93%; лимит 2.1 млрд DOT; номинаторы без slashing | текущее / правило | — | [Staking Rewards](https://www.stakingrewards.com/asset/polkadot), [форум](https://forum.polkadot.network/t/polkadot-staking-changes-progress-timeline/17436) |
| Cosmos Hub ~19.7%, инфляция ~10% | текущее | — | [Staking Rewards](https://www.stakingrewards.com/asset/cosmos), [CryptoToolbox](https://cryptotoolbox.io/atom-staking) |
| Требования к железу Ethereum | правило (рекомендация) | — | [EIP-7870](https://eips.ethereum.org/EIPS/eip-7870), [ethereum.org](https://ethereum.org/roadmap/statelessness/), [EF: partial history expiry](https://blog.ethereum.org/2025/07/08/partial-history-exp) |
| Glamsterdam: Sepolia 06.10.2026, Hoodi отложен, даты для mainnet нет; Fusaka активен с 03.12.2025 | текущее | — | [EF blog](https://blog.ethereum.org/category/protocol), [ethereum.org](https://ethereum.org/roadmap/glamsterdam/) |

## Рестейкинг, кредитование, стейблкоины

| Данные | Тип | Источник |
|---|---|---|
| TVL EigenLayer $22.06 млрд → $5.10 млрд; Symbiotic $2.70 млрд → $342.8 млн | историческое | [TokenAlphabet](https://tokenalphabet.com/blog/eigenlayer-vs-symbiotic-competing-visions-of-restaking) |
| Выплаты EigenLayer: Q4 2024 $63.28M → Q2 2026 $2.5M | историческое (по DefiLlama) | [BlockchainDose](https://blockchaindose.com/restaking-fees/) |
| ether.fi убрал рестейкинг из weETH (август 2026) | историческое | [CoinDesk](https://www.coindesk.com/business/2026/09/28/the-restaking-gold-rush-is-over-and-top-protocols-are-barely-making-a-profit) |
| Слешинг EigenLayer с 17.04.2025; redistributable slashing | правило | [EigenCloud docs](https://docs.eigencloud.xyz/eigenlayer/concepts/slashing/slashing-concept) |
| Aave v3 USDC: 3.51% supply APR, загрузка 90.3%; средние за 7, 30, 180, 365 дней | текущее / историческое (без исторических стимулов) | [Aavescan](https://aavescan.com/ethereum-v3/usdc) |
| Sky Savings Rate 3.80% с 07.10.2026; история ставок | текущее / историческое | [sky.money](https://sky.money/susds), [Rails](https://rails.finance/ethereum/sky-savings/rates) |
| sUSDe 5.01%; история депозитов | текущее / историческое | [Aavescan](https://aavescan.com/rates/ethena-susde) |
| Pendle PT-sUSDe 5.13% до 25.11.2026 | текущее (фиксируется при покупке) | [Pendle](https://app.pendle.finance/trade/markets/0x47ad2cd1dd15739a7a035b9d3b7828d916fef77e/limit-order/buy) |
| Ставки USDC по протоколам | текущее | [AlphaGrowth](https://alphagrowth.io/apr/tokens/usdc) |
| CEX Earn USDT | текущее (08.11.2026) | [Jason Finance](https://jason-finance.com/en/tools/usdt-earn-rates/), [Kevin Wu (13.10.2026)](https://kevin-wu.org/en/usdt-earn-rates-en/) |
| Долларовые ОВДП 3.6–4.12%; гривневые 17.2–17.8% | текущее | [Finomo](https://finomo.com.ua/ovdp) |
| Налогообложение ОВДП и депозитов | правило | [ГРОШІ pro](https://groshipro.com.ua/rynky/depozyt-ovdp-chy-valiuta) |
| Условия Ethena, Sky, Lido по юрисдикциям | правило | [Ethena](https://docs.ethena.fi/resources/terms-of-service), [Sky](https://docs.sky.money/legal/skybase-international/terms-of-use), [Lido](https://lido.fi/terms-of-use) |

## LP, деривативы, трейдинг

| Данные | Тип | Источник |
|---|---|---|
| Uniswap v3: $41.6M комиссий, −$20.4M против удержания после газа за 12 месяцев | историческое (до 13.10.2026) | [Bitquery](https://bitquery.io/investigations/uniswap-v3-lp-returns) |
| Uniswap v4: 73% пулов с отрицательным результатом LP | историческое (август 2026) | [Dune](https://dune.com/amplifiliq/uniswap-v4-pool-profitability-who-actually-makes-money-for-lps) |
| Fee APR ранжирует пулы наоборот | историческое (37 недель 2026) | [SSRN](https://papers.ssrn.com/sol3/Delivery.cfm/7499641.pdf?abstractid=7499641&mirid=1) |
| 7-дневные бэктесты LP | историческое (7 дней до 08.11.2026; лучший диапазон выбран задним числом) | [LPSignal](https://lpsignal.app/reports/lp-returns) |
| HLP: APR −0.02%, TVL $148.3M; 94 дня 3.75% | текущее / историческое | [Hyperliquid](https://app.hyperliquid.xyz/vaults), [Cipher Intelligence](https://cipher-intelligence.io/blog/hyperliquid-vaults/) |
| HLP +54.9% в год за всю историю | историческое (с поправкой на потоки) | [PerpVault](https://perpvault.com/vault.html?id=hyperliquid%3A0xdfc24b077bc1425ad1dea75bcb6f8158e10df303) |
| Фандинг BTC 0.0060% за 8 ч в среднем по 29 биржам | текущее (12:58 UTC) | [CoinClass](https://coinclass.com/funding-rate) |
| Копи-трейдинг: 31% подписчиков в плюсе, медиана −25.2% | историческое | [Botsfolio](https://botsfolio.com/blog/does-copy-trading-work) |
| MEV: три сёрчера ~73% CEX-DEX MEV | историческое (08.2023–03.2025) | [arXiv 2507.13023](https://arxiv.org/html/2507.13023) |
| Конкуренция сёрчеров и доля валидатора | исследование | [ACM TWeb](https://dl.acm.org/doi/full/10.1145/3840300) |

## Инфраструктура и DePIN

| Данные | Тип | Источник |
|---|---|---|
| Hashprice $32.3 за PH/s в сутки; −21.8% за год; сеть ~1,062 EH/s | текущее / историческое | [Orange Abacus](https://www.orangeabacus.com/bitcoin-hashprice-tracker/), [Hashrate Index](https://hashrateindex.com/blog/hashrate-index-roundup-november-2-2026/) |
| Тариф 4.32 грн/кВт·ч до 30.04.2027; ночной 2.16 | правило | [Факты ICTV](https://fakty.com.ua/ua/ukraine/ekonomika/20261101-taryf-na-svitlo-z-1-lystopada-chy-dovedetsya-ukrayintsyam-platyty-bilshe/) |
| Цены bare metal: Cherry Servers $240–280 за 4 ТБ/64 ГБ | текущее | [Cherry Servers](https://www.cherryservers.com/blog/ethereum-node-cost) |
| Hetzner: запрет крипто-нагрузок | правило (формулировка поддержки 2022 года, подтверждена в обзоре 2026 года) | [Hetzner](https://www.hetzner.com/legal/dedicated-server/), [Reddit (цитата поддержки)](https://www.reddit.com/r/hetzner/comments/wucxs4/is_it_allowed_to_run_a_crypto_block_chain_node/), [OrbitServers](https://orbitservers.io/blog/crypto-friendly-hosting-solana-validators-hetzner-alternative) |
| Storj: $1.35 / $1.00 / $1.00 с 01.09.2026; удержание | правило | [Storj payouts](https://storj.dev/node/payouts), [held amount](https://storj.dev/node/faq/held-back-amount) |
| Mysterium: комиссия 20%; отзыв ~$1.5 в месяц | правило / отзыв | [FAQ](https://docs.mysterium.network/faq), [PassiveIncomeApps](https://passiveincomeapps.com/apps/mysterium) |
| Akash Q1 2026: $253k выручки, 58 провайдеров, загрузка GPU 33.7% | историческое | [Blockworks](https://app.blockworks.com/report/state-of-akash-q1-2026-final) |
| The Graph: минимальный залог 100k GRT | правило | [The Graph docs](https://thegraph.com/docs/en/indexing/overview/) |
| Pocket: 59,500 POKT, 79% поставщикам | правило | [Pocket docs](https://docs.pocket.network/node-operators/rewards-economics/) |
| Chainlink: официальные операторы отбираются Chainlink Labs | правило | [LinkWell](https://docs.linkwellnodes.io/knowledgebase/faq/Chainlink-Operators), [Chainlink staking](https://chain.link/economics/staking) |
| Succinct и Boundless: экономика проверов | правило / анализ | [Succinct](https://docs.succinct.xyz/docs/provers/setup/faq), [Boundless](https://docs.boundless.network/zkc/mining/overview), [CFLabs](https://cflabs.ai/research/the-prover-network-landscape-a-comparative-analysis-of-succint-and-boundless-networks/) |
| SSV: permissionless-операторы, оплата в ETH | правило | [SSV docs](https://docs.ssv.network/learn/tokenomics/) |

## Навыки и рынок труда

| Данные | Тип | Источник |
|---|---|---|
| 72 роли, медиана середины вилок $203k | текущее (07.11.2026; вилки работодателей) | [ChainJobs](https://chainjobs.io/roles/infrastructure-engineer/) |
| Backend/infra медиана $203k по 131 вакансии | текущее | [Jobs Web3](https://jobsweb3.io/web3-salaries/backend-engineer) |
| Senior DevOps в Украине $5,100 после налогов | историческое (опрос май–июнь 2026) | [DOU](https://dou.ua/lenta/articles/salary-report-devops-summer-2026/) |
| DevOps в Украине: медиана вакансий $5,500, Senior $6,000 | текущее (05.11.2026; обычно до налогов) | [Zapit](https://zapit.work/en/role/devops-engineer) |
| Immunefi: $144.7M всего, Q3 2026 $4.6M | историческое | [GlobeNewswire](https://www.globenewswire.com/news-release/2026/11/04/3395605/0/en/crypto-hacks-put-security-costs-in-perspective-as-immunefi-researcher-payouts-rise-54.html) |
| Хакатоны ETHGlobal 2026 | историческое | [Medalist](https://medalist.build/hackathons) |
| EF ESP: нет открытых программ | текущее | [ESP](https://esp.ethereum.foundation/applicants/wishlist) |

## Airdrops, токенсейлы, мемкоины, инциденты

| Данные | Тип | Источник |
|---|---|---|
| 51 airdrop в 2026: $809.4M на 2.02M кошельков | историческое | [CoinLaw (Bitquery)](https://coinlaw.io/token-airdrop-statistics/) |
| Медианы прошлых airdrop | историческое | [Does It Pay?](https://doesitpay.org/airdrop-farming/research/) |
| Фильтры против Sybil | историческое | [dificalc](https://dificalc.com/blog/defi-airdrop-farming-2026) |
| Токенсейлы: 24% с положительной доходностью | историческое | [Blockworks Intel](https://app.blockworks.com/report/an-analysis-of-public-token-sales) |
| Листинги с FDV выше $1 млрд: медиана −81% за год | историческое | [GSR](https://www.gsr.io/insights/beyond-low-float-high-fdv-what-better-token-launches-look-like) |
| Мемкоины Solana: 74% покупателей в минусе | историческое (11.2025–08.2026) | [Bitquery](https://bitquery.io/investigations/solana-memecoin-traders-lose-money) |
| Взломы 2026: $8.78 млрд, 333 инцидента | текущее (без вычета возвращённых средств) | [DefiLlama](https://defillama.com/hacks) |
| Binance: инцидент 29.10.2026 | историческое | [объявление](https://www.binance.com/en/support/announcement/detail/c5a8729a97ac486d963784d96c5642d7), [блог](https://www.binance.com/en/blog/community/3229153443759566763), [CNBC](https://www.cnbc.com/2026/10/31/binance-hack-asset-coverage-withdrawals.html) |

## Украина: право и налоги

| Данные | Тип | Источник |
|---|---|---|
| Законопроект 10225-д: статус и положения | текущее (законопроект, не закон) | [карточка ВРУ](https://itd.rada.gov.ua/billinfo/Bills/Card/56271), [Лига.Закон](https://biz.ligazakon.net/news/247086_podatki-na-kriptu-z-1-lipnya-2027-roku-komtet-pdtrimav-zakonoprokt--10225-d), [Укрінформ](https://www.ukrinform.ua/rubric-economy/4181341-komitet-radi-rekomenduvav-uhvaliti-zakonoproekt-pro-reguluvanna-rinku-virtualnih-aktiviv) |
| Позиция ДПС о доходе от крипты | правило (ИПК) | [ИПК 5352](https://zvit.vchasno.ua/taxes-consultation/opodatkuvannia-kryptovaliuty-pozytsiia-dps-1975314/), [ДПС Львов](https://lv.tax.gov.ua/media-ark/news-ark/667492.html) |
| ФЛП и криптовалюта | правило (разъяснение ДПС) | [ДПС Львов](https://lv.tax.gov.ua/media-ark/news-ark/710630.html), [Лига.Закон](https://biz.ligazakon.net/news/245599_oplata-v-usdt-vd-nozemnikh-platform-chomu-fop-ne-mozhe-vklyuchiti-takiy-dokhd-do-dinogo-podatku) |
| Военный сбор, ЕСВ, минимальная зарплата 2026 | правило | [ДПС Полтава](https://poltava.tax.gov.ua/media-ark/news-ark/984783.html), [ДПС Киевская обл.](https://kyivobl.tax.gov.ua/media-ark/news-ark/965745.html) |
| НБУ: покупка крипты, P2P, меморандум | правило (по разборам юристов и СМИ) | [Mind](https://mind.ua/openmind/20307683-yak-ukrayincyu-zakonno-pridbati-kriptovalyutu), [meretskyi](https://www.meretskyi.com/uk/2026/08/18/limity-nbu-na-pokupku-kriptovalyuty-s-karty/) |
| Binance закрывает Fiat Trade UAH | правило (объявление 23.09.2026) | [копия объявления](https://tokenearly.com/announcement/6ab3790f73cff99d464d9111.html), [dev.ua](https://dev.ua/en/news/binance-prypyniaie-pidtrymku-hryvni-1790151162) |

## Версии ПО (проверены через GitHub API и Docker Hub 2026-11-08)

Nethermind 2.2.2 · Lighthouse v8.3.2 · Geth v1.17.10 · Nimbus v26.10.2 · MEV-Boost 1.12 (тег образа без `v`) · Prometheus v3.16.0 · Alertmanager v0.34.2 · Grafana 13.3.0 · node_exporter v1.12.1 · blackbox_exporter v0.29.1 · ethstaker-deposit-cli v1.3.0. Флаги клиентов сверены с [документацией Nethermind](https://docs.nethermind.io/fundamentals/configuration/), Lighthouse book ([bn](https://lighthouse-book.sigmaprime.io/help_bn.html), [vc](https://lighthouse-book.sigmaprime.io/help_vc.html)), README MEV-Boost v1.12 и [deposit-cli](https://deposit-cli.ethstaker.cc/new_mnemonic.html).

---

## Что не проверено и как это влияет на выводы

| Пункт | Влияние |
|---|---|
| Доступность для резидента Украины: Aave, Pendle, Uniswap, Curve, Storj, Mysterium, Pocket, The Graph, SSV, Akash, Succinct, Boundless, интерфейс Rocket Pool, депозит Gnosis; ICS для украинских заявителей | перед использованием прочитать условия; если ограничение есть — направление отпадает |
| OKX: официальный список ограничений; продолжение работы Binance P2P с гривной; лимиты меморандума банков | взяты из вторичных источников; проверить в интерфейсе и у банка |
| Ставки фриланса, документации, услуг и цены продукта мониторинга | модели в K02, K03, K06 — допущения; проверяются разговорами с клиентами |
| Цены железа в Украине (мини-ПК, RAM, NVMe, ИБП) и ASIC ($3,500) | меняют окупаемость; вывод по майнингу от цены ASIC не зависит (он отрицателен и при нулевой цене железа на дневном тарифе) |
| Допустимость бытового тарифа для майнинга | правовой вопрос к поставщику электроэнергии |
| Как украинское право об азартных играх квалифицирует Polymarket | правовой вопрос |
| Текущие суммы платы за подачу отчётов в Immunefi | влияет на стоимость входа в bug bounty |
| Длительность отчётного периода CSM и пороги страйков для 0x01 | влияет на сроки первой выплаты и риск штрафа |
| Статус slashing для делегаторов Solana в 2026 году | влияет на оценку риска нативного стейкинга SOL |
| Минимальный депозит HLP и детали официального моста Hyperliquid | операционная деталь |
| Размеры контрактов и премии опционов | расчёт covered calls не делался |
| Доступность токенизированных казначейских бумаг (BUIDL, USDY и др.) для резидента Украины | направление E6 помечено «при условиях» |
| NFT, GameFi, SocialFi, Grass и другие bandwidth-DePIN, learn-and-earn | свежие данные не собирались; оценка качественная |
| Точная дата форка Gnosis EEZ | влияет на срок жизни учебного валидатора Gnosis |

## Вопросы к вам, ответы на которые изменили бы рекомендации

1. **Есть ли у вас уже ETH или другие криптоактивы, и какова их себестоимость?** Если вы долгосрочно держите ETH, CSM (ICS, 6+ ключей) и stETH становятся разумными; кроме того, переходная ставка 5% по законопроекту касается именно ранее купленных активов.
2. **Работаете ли вы сейчас по найму или как ФЛП, и что говорит договор о подработке и неконкуренции?** Это определяет, можно ли брать контракты и клиентов.
3. **Сколько часов в неделю и на какой срок вы реально готовы выделять?** Ниже ~8 часов в неделю услуги для клиентов (K02) нереалистичны.
4. **Есть ли дома ИБП или генератор, резервный интернет, белый IP?** Без них домашний mainnet-валидатор и Storj отпадают, остаются Hoodi и аренда.
5. **Уровень английского и готовность к интервью, созвонам и продажам?** Влияет на выбор между глобальным рынком (K01) и украинским, а также на реалистичность K02.
6. **Готовы ли вы к дежурствам для клиентов?** Без этого K02 сводится к разовым установкам.
7. **Есть ли свободный капитал, когда он может понадобиться и какую сумму вы готовы потерять без вреда?** Определяет, есть ли смысл в K10 и CSM на mainnet.
8. **Планируете ли выезд или смену налогового резидентства?** Меняет весь налоговый раздел.
9. **Принимаете ли вы оплату только в фиате?** Если да, баунти и bug bounty с выплатами в токенах менее удобны.
10. **Есть ли опыт Solidity, Rust или Go?** Без него bug bounty потребует долгой подготовки.
11. **Есть ли всё-таки свободные серверы или GPU?** Если да, пересчитываются Akash, проверы и другие роли раздела H.
