<template>
	<div class="home-page">
		<!-- Hero Section -->
		<div class="hero-section text-center mb-8">
			<div class="hero-content">
				<div class="hero-icon mb-4">
					<div class="icon-wrapper">
						<v-icon size="64" class="hero-main-icon">mdi-calculator-variant</v-icon>
						<div class="icon-glow"></div>
					</div>
				</div>
				<h1 class="hero-title text-5xl font-bold mb-3">Hôm Nay Ăn Gì</h1>
				<p class="hero-subtitle text-xl mb-6">Thống kê chi tiêu nhóm vui vẻ</p>

				<!-- Overview Stats -->
				<div v-if="stats" class="quick-stats mb-4">
					<v-row justify="center" dense>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-primary">
									{{ formatCurrency(stats.overview.total_spending) }}
								</div>
								<div class="stats-label text-sm">Tổng chi tiêu</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-secondary">{{ stats.overview.total_expenses }}</div>
								<div class="stats-label text-sm">Khoản chi</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-success">{{ stats.overview.total_paid }}</div>
								<div class="stats-label text-sm">Đã trả</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-error">{{ stats.overview.total_unpaid }}</div>
								<div class="stats-label text-sm">Chưa trả</div>
							</v-card>
						</v-col>
					</v-row>
				</div>
			</div>
		</div>

		<div v-if="loading" class="d-flex justify-center py-12">
			<v-progress-circular indeterminate color="primary" size="48" />
		</div>

		<template v-else-if="stats">
			<!-- Fun Leaderboards -->
			<div class="section-header mb-4">
				<h2 class="text-2xl font-bold">Bảng xếp hạng vui</h2>
				<p class="text-sm text-medium-emphasis">Nhấn vào thẻ để xem top 10</p>
			</div>

			<v-row class="mb-8">
				<v-col cols="12" sm="6" md="4" v-for="card in leaderboardCards" :key="card.key">
					<v-card
						v-if="card.top"
						class="leaderboard-card h-100 clickable-card"
						rounded="xl"
						elevation="0"
						@click="openRanking(card)"
					>
						<div class="card-accent" :class="card.accentClass"></div>
						<v-card-text class="pa-5">
							<div class="d-flex align-center mb-3">
								<v-icon :color="card.color" size="28" class="mr-2">{{ card.icon }}</v-icon>
								<span class="text-caption font-weight-bold text-uppercase" style="letter-spacing: 1px">{{ card.title }}</span>
								<v-spacer />
								<v-icon size="16" color="grey">mdi-chevron-right</v-icon>
							</div>
							<div class="d-flex align-center mb-3">
								<v-avatar size="48" class="mr-3" :color="card.avatarBg">
									<v-img v-if="card.top.avatar || card.top.payer_avatar || card.top.member_avatar"
										:src="card.top.avatar || card.top.payer_avatar || card.top.member_avatar" />
									<v-icon v-else :color="card.color">{{ card.fallbackIcon }}</v-icon>
								</v-avatar>
								<div>
									<div class="font-weight-bold text-lg">{{ card.top.name || card.top.member_name || card.top.payer_name }}</div>
									<div class="text-caption text-medium-emphasis">{{ card.subtitle(card.top) }}</div>
								</div>
							</div>
							<div class="text-h5 font-weight-bold" :class="card.valueColor">
								{{ card.valueDisplay(card.top) }}
							</div>
						</v-card-text>
					</v-card>
				</v-col>
			</v-row>

			<!-- Charts Section -->
			<div v-if="stats.charts.monthly_spending.length > 0 || stats.charts.spending_by_payer.length > 0">
				<div class="section-header mb-4">
					<h2 class="text-2xl font-bold">Biểu đồ</h2>
				</div>
				<v-row class="mb-8">
					<v-col cols="12" md="7" v-if="stats.charts.monthly_spending.length > 0">
						<v-card class="chart-card pa-5" rounded="xl" elevation="0">
							<h3 class="text-lg font-weight-bold mb-4">
								<v-icon class="mr-2" color="primary">mdi-chart-line</v-icon>
								Chi tiêu theo tháng
							</h3>
							<div class="chart-container"><Bar :data="monthlyChartData" :options="barChartOptions" /></div>
						</v-card>
					</v-col>
					<v-col cols="12" md="5" v-if="stats.charts.spending_by_payer.length > 0">
						<v-card class="chart-card pa-5" rounded="xl" elevation="0">
							<h3 class="text-lg font-weight-bold mb-4">
								<v-icon class="mr-2" color="secondary">mdi-chart-pie</v-icon>
								Ai trả nhiều nhất
							</h3>
							<div class="chart-container"><Doughnut :data="payerChartData" :options="doughnutChartOptions" /></div>
						</v-card>
					</v-col>
				</v-row>
			</div>
		</template>

		<!-- Empty State -->
		<div v-else-if="!loading" class="empty-state">
			<v-card class="empty-card text-center pa-12" rounded="xl" elevation="0">
				<v-icon size="96" color="surface-variant">mdi-chart-box-outline</v-icon>
				<h3 class="text-2xl font-bold mb-4 mt-4">Chưa có dữ liệu</h3>
				<p class="text-lg text-on-surface-variant">Hãy tạo khoản chi tiêu đầu tiên!</p>
			</v-card>
		</div>

		<!-- Ranking Dialog -->
		<v-dialog v-model="rankingDialog" max-width="520px" scrollable>
			<v-card rounded="xl" v-if="activeRanking">
				<div class="ranking-header pa-5 pb-3">
					<div class="d-flex align-center">
						<v-icon :color="activeRanking.color" size="28" class="mr-3">{{ activeRanking.icon }}</v-icon>
						<div>
							<h3 class="text-xl font-weight-bold">{{ activeRanking.title }}</h3>
							<p class="text-caption text-medium-emphasis">Top {{ activeRanking.items.length }}</p>
						</div>
						<v-spacer />
						<v-btn icon variant="text" @click="rankingDialog = false"><v-icon>mdi-close</v-icon></v-btn>
					</div>
				</div>
				<v-divider />
				<v-card-text class="pa-0">
					<v-list lines="two">
						<v-list-item
							v-for="(item, idx) in activeRanking.items"
							:key="idx"
							class="ranking-item"
						>
							<template v-slot:prepend>
								<div class="rank-badge mr-3" :class="{ 'rank-gold': idx === 0, 'rank-silver': idx === 1, 'rank-bronze': idx === 2 }">
									{{ idx + 1 }}
								</div>
								<v-avatar size="40" :color="activeRanking.avatarBg" class="mr-3">
									<v-img v-if="item.avatar || item.payer_avatar || item.member_avatar"
										:src="item.avatar || item.payer_avatar || item.member_avatar" />
									<v-icon v-else :color="activeRanking.color" size="20">{{ activeRanking.fallbackIcon }}</v-icon>
								</v-avatar>
							</template>
							<v-list-item-title class="font-weight-medium">
								{{ item.name || item.member_name || item.payer_name }}
							</v-list-item-title>
							<v-list-item-subtitle>{{ activeRanking.subtitle(item) }}</v-list-item-subtitle>
							<template v-slot:append>
								<span class="font-weight-bold" :class="activeRanking.valueColor">
									{{ activeRanking.valueDisplay(item) }}
								</span>
							</template>
						</v-list-item>
					</v-list>
				</v-card-text>
			</v-card>
		</v-dialog>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { statsApi } from "../services/api";
import { Bar, Doughnut } from "vue-chartjs";
import {
	Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const stats = ref<any>(null);
const loading = ref(true);
const rankingDialog = ref(false);
const activeRanking = ref<any>(null);

const CHART_COLORS = [
	"#667eea", "#764ba2", "#f093fb", "#43e97b", "#fa709a",
	"#fee140", "#30cfd0", "#a18cd1", "#fbc2eb", "#ff9a9e",
];

const fetchStats = async () => {
	loading.value = true;
	try {
		const response = await statsApi.getPublicStats();
		stats.value = response.data;
	} catch (error) {
		console.error("Error fetching stats:", error);
	} finally {
		loading.value = false;
	}
};

const formatCurrency = (amount: number) => {
	return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(amount);
};

// Leaderboard card definitions — each maps to an array from the API
const leaderboardCards = computed(() => {
	if (!stats.value) return [];
	const lb = stats.value.leaderboards;
	return [
		{
			key: "top_spenders",
			title: "Đại gia",
			icon: "mdi-crown",
			color: "amber",
			accentClass: "accent-gold",
			avatarBg: "amber-lighten-4",
			fallbackIcon: "mdi-cash-multiple",
			valueColor: "text-amber-darken-2",
			items: lb.top_spenders || [],
			top: lb.top_spenders?.[0] || null,
			subtitle: (item: any) => `${item.count} lần trả`,
			valueDisplay: (item: any) => formatCurrency(item.total),
		},
		{
			key: "top_debtors",
			title: "Nợ nhiều nhất",
			icon: "mdi-alert-circle",
			color: "error",
			accentClass: "accent-red",
			avatarBg: "red-lighten-4",
			fallbackIcon: "mdi-emoticon-cry",
			valueColor: "text-error",
			items: lb.top_debtors || [],
			top: lb.top_debtors?.[0] || null,
			subtitle: (item: any) => `${item.debt_count} khoản nợ`,
			valueDisplay: (item: any) => formatCurrency(item.total_owed),
		},
		{
			key: "most_generous",
			title: "Hay bao nhất",
			icon: "mdi-heart",
			color: "success",
			accentClass: "accent-green",
			avatarBg: "green-lighten-4",
			fallbackIcon: "mdi-hand-heart",
			valueColor: "text-success",
			items: lb.most_generous || [],
			top: lb.most_generous?.[0] || null,
			subtitle: (item: any) => `${item.count} lần bao`,
			valueDisplay: (item: any) => formatCurrency(item.total),
		},
		{
			key: "longest_debts",
			title: "Nợ lâu nhất",
			icon: "mdi-timer-sand",
			color: "purple",
			accentClass: "accent-purple",
			avatarBg: "purple-lighten-4",
			fallbackIcon: "mdi-sleep",
			valueColor: "text-purple",
			items: lb.longest_debts || [],
			top: lb.longest_debts?.[0] || null,
			subtitle: (item: any) => item.expense_name,
			valueDisplay: (item: any) => `${item.days_ago} ngày (${formatCurrency(item.amount)})`,
		},
		{
			key: "biggest_meals",
			title: "Bữa ăn đắt nhất",
			icon: "mdi-food",
			color: "orange",
			accentClass: "accent-orange",
			avatarBg: "orange-lighten-4",
			fallbackIcon: "mdi-silverware-fork-knife",
			valueColor: "text-orange-darken-2",
			items: lb.biggest_meals || [],
			top: lb.biggest_meals?.[0] || null,
			subtitle: (item: any) => `${item.payer_name} trả — ${item.participant_count} người`,
			valueDisplay: (item: any) => formatCurrency(item.amount),
		},
		{
			key: "cleanest_members",
			title: "Sạch nợ nhất",
			icon: "mdi-star",
			color: "teal",
			accentClass: "accent-teal",
			avatarBg: "teal-lighten-4",
			fallbackIcon: "mdi-check-decagram",
			valueColor: "text-teal",
			items: lb.cleanest_members || [],
			top: lb.cleanest_members?.[0] || null,
			subtitle: () => "Chỉ nợ có",
			valueDisplay: (item: any) => formatCurrency(item.total_owed),
		},
	].filter((c) => c.top);
});

const openRanking = (card: any) => {
	activeRanking.value = card;
	rankingDialog.value = true;
};

// --- Charts ---
const monthlyChartData = computed(() => {
	if (!stats.value) return { labels: [], datasets: [] };
	const data = stats.value.charts.monthly_spending;
	return {
		labels: data.map((item: any) => { const [y, m] = item.month.split("-"); return `T${m}/${y}`; }),
		datasets: [{
			label: "Chi tiêu (VND)",
			data: data.map((item: any) => item.total),
			backgroundColor: "rgba(102, 126, 234, 0.7)",
			borderColor: "#667eea",
			borderWidth: 2,
			borderRadius: 8,
		}],
	};
});

const payerChartData = computed(() => {
	if (!stats.value) return { labels: [], datasets: [] };
	const data = stats.value.charts.spending_by_payer;
	return {
		labels: data.map((item: any) => item.name),
		datasets: [{
			data: data.map((item: any) => item.total),
			backgroundColor: CHART_COLORS.slice(0, data.length),
			borderWidth: 2,
			borderColor: "#fff",
		}],
	};
});

const barChartOptions = {
	responsive: true,
	maintainAspectRatio: false,
	plugins: {
		legend: { display: false },
		tooltip: { callbacks: { label: (ctx: any) => formatCurrency(ctx.parsed.y) } },
	},
	scales: {
		y: {
			beginAtZero: true,
			ticks: { callback: (val: any) => val >= 1000000 ? `${val / 1000000}M` : val >= 1000 ? `${val / 1000}K` : val },
			grid: { color: "rgba(0,0,0,0.05)" },
		},
		x: { grid: { display: false } },
	},
};

const doughnutChartOptions = {
	responsive: true,
	maintainAspectRatio: false,
	plugins: {
		legend: { position: "bottom" as const, labels: { padding: 16, usePointStyle: true } },
		tooltip: { callbacks: { label: (ctx: any) => `${ctx.label}: ${formatCurrency(ctx.parsed)}` } },
	},
};

onMounted(fetchStats);
</script>

<style scoped>
.home-page { max-width: 1200px; margin: 0 auto; }

.hero-section { position: relative; padding: 3rem 0 1rem; }
.hero-content { position: relative; z-index: 2; }
.hero-icon { position: relative; display: inline-block; }
.icon-wrapper { position: relative; display: inline-block; }

.hero-main-icon {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
}

.icon-glow {
	position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
	width: 120px; height: 120px;
	background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
	border-radius: 50%; animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
	0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
	50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.8; }
}

.hero-title {
	background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
	-webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2;
}
.hero-subtitle { color: rgb(107, 114, 128); }

.stats-card {
	background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1); transition: transform 0.2s ease; min-width: 110px;
}
.stats-card:hover { transform: translateY(-2px); }
.stats-label { color: rgb(107, 114, 128); font-weight: 500; }
.section-header { text-align: left; }

/* Leaderboard cards */
.leaderboard-card {
	background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px);
	border: 1px solid rgba(0, 0, 0, 0.06); position: relative; overflow: hidden; transition: all 0.3s ease;
}
.clickable-card { cursor: pointer; }
.clickable-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1); }

.card-accent { position: absolute; top: 0; left: 0; right: 0; height: 4px; }
.accent-gold { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.accent-red { background: linear-gradient(90deg, #ef4444, #f87171); }
.accent-green { background: linear-gradient(90deg, #10b981, #34d399); }
.accent-purple { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.accent-orange { background: linear-gradient(90deg, #f97316, #fb923c); }
.accent-teal { background: linear-gradient(90deg, #14b8a6, #2dd4bf); }

/* Ranking dialog */
.ranking-header { background: rgba(255, 255, 255, 0.95); }
.rank-badge {
	width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
	font-weight: 700; font-size: 0.8rem; background: rgba(0, 0, 0, 0.06); color: rgba(0, 0, 0, 0.5);
}
.rank-gold { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; }
.rank-silver { background: linear-gradient(135deg, #9ca3af, #d1d5db); color: white; }
.rank-bronze { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }
.ranking-item { border-bottom: 1px solid rgba(0, 0, 0, 0.04); }

/* Charts */
.chart-card {
	background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px);
	border: 1px solid rgba(0, 0, 0, 0.06);
}
.chart-container { height: 300px; position: relative; }

/* Empty state */
.empty-state { display: flex; justify-content: center; align-items: center; min-height: 300px; }
.empty-card {
	background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1); max-width: 500px;
}

@media (max-width: 768px) {
	.hero-title { font-size: 2.25rem; }
	.hero-subtitle { font-size: 1.125rem; }
	.stats-card { min-width: 90px; padding: 0.75rem !important; }
}
@media (max-width: 600px) {
	.hero-section { padding: 1.5rem 0 0.5rem; }
	.hero-title { font-size: 1.875rem; }
	.chart-container { height: 250px; }
}
</style>
