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
				<h1 class="hero-title text-5xl font-bold mb-3">Hom Nay An Gi</h1>
				<p class="hero-subtitle text-xl mb-6">
					Thong ke chi tieu nhom vui ve
				</p>

				<!-- Overview Stats -->
				<div v-if="stats" class="quick-stats mb-4">
					<v-row justify="center" dense>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-primary">
									{{ formatCurrency(stats.overview.total_spending) }}
								</div>
								<div class="stats-label text-sm">Tong chi tieu</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-secondary">
									{{ stats.overview.total_expenses }}
								</div>
								<div class="stats-label text-sm">Khoan chi</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-success">
									{{ stats.overview.total_paid }}
								</div>
								<div class="stats-label text-sm">Da tra</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card class="stats-card pa-4 mx-1" rounded="xl" elevation="0">
								<div class="stats-number text-2xl font-bold text-error">
									{{ stats.overview.total_unpaid }}
								</div>
								<div class="stats-label text-sm">Chua tra</div>
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
				<h2 class="text-2xl font-bold">Bang xep hang vui</h2>
			</div>

			<v-row class="mb-8">
				<!-- Top Spender -->
				<v-col cols="12" sm="6" md="4" v-if="stats.leaderboards.top_spender">
					<v-card class="leaderboard-card h-100" rounded="xl" elevation="0">
						<div class="card-accent accent-gold"></div>
						<v-card-text class="pa-5">
							<div class="d-flex align-center mb-3">
								<v-icon color="amber" size="28" class="mr-2">mdi-crown</v-icon>
								<span class="text-caption font-weight-bold text-uppercase" style="letter-spacing: 1px">Dai gia</span>
							</div>
							<div class="d-flex align-center mb-3">
								<v-avatar size="48" class="mr-3" color="amber-lighten-4">
									<v-img v-if="stats.leaderboards.top_spender.avatar" :src="stats.leaderboards.top_spender.avatar" />
									<v-icon v-else color="amber">mdi-cash-multiple</v-icon>
								</v-avatar>
								<div>
									<div class="font-weight-bold text-lg">{{ stats.leaderboards.top_spender.name }}</div>
									<div class="text-caption text-medium-emphasis">{{ stats.leaderboards.top_spender.count }} lan tra</div>
								</div>
							</div>
							<div class="text-h5 font-weight-bold text-amber-darken-2">
								{{ formatCurrency(stats.leaderboards.top_spender.total) }}
							</div>
						</v-card-text>
					</v-card>
				</v-col>

				<!-- Top Debtor -->
				<v-col cols="12" sm="6" md="4" v-if="stats.leaderboards.top_debtor">
					<v-card class="leaderboard-card h-100" rounded="xl" elevation="0">
						<div class="card-accent accent-red"></div>
						<v-card-text class="pa-5">
							<div class="d-flex align-center mb-3">
								<v-icon color="error" size="28" class="mr-2">mdi-alert-circle</v-icon>
								<span class="text-caption font-weight-bold text-uppercase" style="letter-spacing: 1px">No nhieu nhat</span>
							</div>
							<div class="d-flex align-center mb-3">
								<v-avatar size="48" class="mr-3" color="red-lighten-4">
									<v-img v-if="stats.leaderboards.top_debtor.avatar" :src="stats.leaderboards.top_debtor.avatar" />
									<v-icon v-else color="error">mdi-emoticon-cry</v-icon>
								</v-avatar>
								<div>
									<div class="font-weight-bold text-lg">{{ stats.leaderboards.top_debtor.name }}</div>
									<div class="text-caption text-medium-emphasis">{{ stats.leaderboards.top_debtor.debt_count }} khoan no</div>
								</div>
							</div>
							<div class="text-h5 font-weight-bold text-error">
								{{ formatCurrency(stats.leaderboards.top_debtor.total_owed) }}
							</div>
						</v-card-text>
					</v-card>
				</v-col>

				<!-- Most Generous -->
				<v-col cols="12" sm="6" md="4" v-if="stats.leaderboards.most_generous">
					<v-card class="leaderboard-card h-100" rounded="xl" elevation="0">
						<div class="card-accent accent-green"></div>
						<v-card-text class="pa-5">
							<div class="d-flex align-center mb-3">
								<v-icon color="success" size="28" class="mr-2">mdi-heart</v-icon>
								<span class="text-caption font-weight-bold text-uppercase" style="letter-spacing: 1px">Hay bao nhat</span>
							</div>
							<div class="d-flex align-center mb-3">
								<v-avatar size="48" class="mr-3" color="green-lighten-4">
									<v-img v-if="stats.leaderboards.most_generous.avatar" :src="stats.leaderboards.most_generous.avatar" />
									<v-icon v-else color="success">mdi-hand-heart</v-icon>
								</v-avatar>
								<div>
									<div class="font-weight-bold text-lg">{{ stats.leaderboards.most_generous.name }}</div>
									<div class="text-caption text-medium-emphasis">{{ stats.leaderboards.most_generous.count }} lan bao</div>
								</div>
							</div>
							<div class="text-h5 font-weight-bold text-success">
								{{ formatCurrency(stats.leaderboards.most_generous.total) }}
							</div>
						</v-card-text>
					</v-card>
				</v-col>

				<!-- Longest Debt -->
				<v-col cols="12" sm="6" md="4" v-if="stats.leaderboards.longest_debt">
					<v-card class="leaderboard-card h-100" rounded="xl" elevation="0">
						<div class="card-accent accent-purple"></div>
						<v-card-text class="pa-5">
							<div class="d-flex align-center mb-3">
								<v-icon color="purple" size="28" class="mr-2">mdi-timer-sand</v-icon>
								<span class="text-caption font-weight-bold text-uppercase" style="letter-spacing: 1px">No lau nhat</span>
							</div>
							<div class="d-flex align-center mb-3">
								<v-avatar size="48" class="mr-3" color="purple-lighten-4">
									<v-img v-if="stats.leaderboards.longest_debt.member_avatar" :src="stats.leaderboards.longest_debt.member_avatar" />
									<v-icon v-else color="purple">mdi-sleep</v-icon>
								</v-avatar>
								<div>
									<div class="font-weight-bold text-lg">{{ stats.leaderboards.longest_debt.member_name }}</div>
									<div class="text-caption text-medium-emphasis">{{ stats.leaderboards.longest_debt.expense_name }}</div>
								</div>
							</div>
							<div class="d-flex align-center">
								<span class="text-h5 font-weight-bold text-purple">{{ stats.leaderboards.longest_debt.days_ago }} ngay</span>
								<span class="text-caption ml-2 text-medium-emphasis">
									({{ formatCurrency(stats.leaderboards.longest_debt.amount) }})
								</span>
							</div>
						</v-card-text>
					</v-card>
				</v-col>

				<!-- Biggest Meal -->
				<v-col cols="12" sm="6" md="4" v-if="stats.leaderboards.biggest_meal">
					<v-card class="leaderboard-card h-100" rounded="xl" elevation="0">
						<div class="card-accent accent-orange"></div>
						<v-card-text class="pa-5">
							<div class="d-flex align-center mb-3">
								<v-icon color="orange" size="28" class="mr-2">mdi-food</v-icon>
								<span class="text-caption font-weight-bold text-uppercase" style="letter-spacing: 1px">Bua an dat nhat</span>
							</div>
							<div class="d-flex align-center mb-3">
								<v-avatar size="48" class="mr-3" color="orange-lighten-4">
									<v-img v-if="stats.leaderboards.biggest_meal.payer_avatar" :src="stats.leaderboards.biggest_meal.payer_avatar" />
									<v-icon v-else color="orange">mdi-silverware-fork-knife</v-icon>
								</v-avatar>
								<div>
									<div class="font-weight-bold text-lg">{{ stats.leaderboards.biggest_meal.name }}</div>
									<div class="text-caption text-medium-emphasis">
										{{ stats.leaderboards.biggest_meal.payer_name }} tra -
										{{ stats.leaderboards.biggest_meal.participant_count }} nguoi
									</div>
								</div>
							</div>
							<div class="text-h5 font-weight-bold text-orange-darken-2">
								{{ formatCurrency(stats.leaderboards.biggest_meal.amount) }}
							</div>
						</v-card-text>
					</v-card>
				</v-col>

				<!-- Cleanest Member -->
				<v-col cols="12" sm="6" md="4" v-if="stats.leaderboards.cleanest_member">
					<v-card class="leaderboard-card h-100" rounded="xl" elevation="0">
						<div class="card-accent accent-teal"></div>
						<v-card-text class="pa-5">
							<div class="d-flex align-center mb-3">
								<v-icon color="teal" size="28" class="mr-2">mdi-star</v-icon>
								<span class="text-caption font-weight-bold text-uppercase" style="letter-spacing: 1px">Sach no nhat</span>
							</div>
							<div class="d-flex align-center mb-3">
								<v-avatar size="48" class="mr-3" color="teal-lighten-4">
									<v-img v-if="stats.leaderboards.cleanest_member.avatar" :src="stats.leaderboards.cleanest_member.avatar" />
									<v-icon v-else color="teal">mdi-check-decagram</v-icon>
								</v-avatar>
								<div>
									<div class="font-weight-bold text-lg">{{ stats.leaderboards.cleanest_member.name }}</div>
									<div class="text-caption text-medium-emphasis">Chi no co</div>
								</div>
							</div>
							<div class="text-h5 font-weight-bold text-teal">
								{{ formatCurrency(stats.leaderboards.cleanest_member.total_owed) }}
							</div>
						</v-card-text>
					</v-card>
				</v-col>
			</v-row>

			<!-- Charts Section -->
			<div v-if="stats.charts.monthly_spending.length > 0 || stats.charts.spending_by_payer.length > 0">
				<div class="section-header mb-4">
					<h2 class="text-2xl font-bold">Bieu do</h2>
				</div>

				<v-row class="mb-8">
					<!-- Monthly Spending Chart -->
					<v-col cols="12" md="7" v-if="stats.charts.monthly_spending.length > 0">
						<v-card class="chart-card pa-5" rounded="xl" elevation="0">
							<h3 class="text-lg font-weight-bold mb-4">
								<v-icon class="mr-2" color="primary">mdi-chart-line</v-icon>
								Chi tieu theo thang
							</h3>
							<div class="chart-container">
								<Bar :data="monthlyChartData" :options="barChartOptions" />
							</div>
						</v-card>
					</v-col>

					<!-- Spending by Payer Chart -->
					<v-col cols="12" md="5" v-if="stats.charts.spending_by_payer.length > 0">
						<v-card class="chart-card pa-5" rounded="xl" elevation="0">
							<h3 class="text-lg font-weight-bold mb-4">
								<v-icon class="mr-2" color="secondary">mdi-chart-pie</v-icon>
								Ai tra nhieu nhat
							</h3>
							<div class="chart-container">
								<Doughnut :data="payerChartData" :options="doughnutChartOptions" />
							</div>
						</v-card>
					</v-col>
				</v-row>
			</div>
		</template>

		<!-- Empty State -->
		<div v-else-if="!loading" class="empty-state">
			<v-card class="empty-card text-center pa-12" rounded="xl" elevation="0">
				<v-icon size="96" color="surface-variant">mdi-chart-box-outline</v-icon>
				<h3 class="text-2xl font-bold mb-4 mt-4">Chua co du lieu</h3>
				<p class="text-lg text-on-surface-variant">
					Hay tao khoan chi tieu dau tien!
				</p>
			</v-card>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { statsApi } from "../services/api";
import { Bar, Doughnut } from "vue-chartjs";
import {
	Chart as ChartJS,
	CategoryScale,
	LinearScale,
	BarElement,
	ArcElement,
	Title,
	Tooltip,
	Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const stats = ref<any>(null);
const loading = ref(true);

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
	return new Intl.NumberFormat("vi-VN", {
		style: "currency",
		currency: "VND",
	}).format(amount);
};

// Monthly spending bar chart data
const monthlyChartData = computed(() => {
	if (!stats.value) return { labels: [], datasets: [] };
	const data = stats.value.charts.monthly_spending;
	return {
		labels: data.map((item: any) => {
			const [y, m] = item.month.split("-");
			return `T${m}/${y}`;
		}),
		datasets: [
			{
				label: "Chi tieu (VND)",
				data: data.map((item: any) => item.total),
				backgroundColor: "rgba(102, 126, 234, 0.7)",
				borderColor: "#667eea",
				borderWidth: 2,
				borderRadius: 8,
			},
		],
	};
});

// Spending by payer doughnut chart data
const payerChartData = computed(() => {
	if (!stats.value) return { labels: [], datasets: [] };
	const data = stats.value.charts.spending_by_payer;
	return {
		labels: data.map((item: any) => item.name),
		datasets: [
			{
				data: data.map((item: any) => item.total),
				backgroundColor: CHART_COLORS.slice(0, data.length),
				borderWidth: 2,
				borderColor: "#fff",
			},
		],
	};
});

const barChartOptions = {
	responsive: true,
	maintainAspectRatio: false,
	plugins: {
		legend: { display: false },
		tooltip: {
			callbacks: {
				label: (ctx: any) => formatCurrency(ctx.parsed.y),
			},
		},
	},
	scales: {
		y: {
			beginAtZero: true,
			ticks: {
				callback: (val: any) => {
					if (val >= 1000000) return `${val / 1000000}M`;
					if (val >= 1000) return `${val / 1000}K`;
					return val;
				},
			},
			grid: { color: "rgba(0,0,0,0.05)" },
		},
		x: { grid: { display: false } },
	},
};

const doughnutChartOptions = {
	responsive: true,
	maintainAspectRatio: false,
	plugins: {
		legend: {
			position: "bottom" as const,
			labels: { padding: 16, usePointStyle: true },
		},
		tooltip: {
			callbacks: {
				label: (ctx: any) => `${ctx.label}: ${formatCurrency(ctx.parsed)}`,
			},
		},
	},
};

onMounted(fetchStats);
</script>

<style scoped>
.home-page {
	max-width: 1200px;
	margin: 0 auto;
}

.hero-section {
	position: relative;
	padding: 3rem 0 1rem;
}

.hero-content {
	position: relative;
	z-index: 2;
}

.hero-icon {
	position: relative;
	display: inline-block;
}

.icon-wrapper {
	position: relative;
	display: inline-block;
}

.hero-main-icon {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
}

.icon-glow {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	width: 120px;
	height: 120px;
	background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
	border-radius: 50%;
	animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
	0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
	50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.8; }
}

.hero-title {
	background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	line-height: 1.2;
}

.hero-subtitle { color: rgb(107, 114, 128); }

.stats-card {
	background: rgba(255, 255, 255, 0.8);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	transition: transform 0.2s ease;
	min-width: 110px;
}

.stats-card:hover { transform: translateY(-2px); }
.stats-label { color: rgb(107, 114, 128); font-weight: 500; }

.section-header { text-align: left; }

/* Leaderboard cards */
.leaderboard-card {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(0, 0, 0, 0.06);
	position: relative;
	overflow: hidden;
	transition: all 0.3s ease;
}

.leaderboard-card:hover {
	transform: translateY(-4px);
	box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.card-accent {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 4px;
}

.accent-gold { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.accent-red { background: linear-gradient(90deg, #ef4444, #f87171); }
.accent-green { background: linear-gradient(90deg, #10b981, #34d399); }
.accent-purple { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.accent-orange { background: linear-gradient(90deg, #f97316, #fb923c); }
.accent-teal { background: linear-gradient(90deg, #14b8a6, #2dd4bf); }

/* Chart cards */
.chart-card {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(0, 0, 0, 0.06);
}

.chart-container {
	height: 300px;
	position: relative;
}

/* Empty state */
.empty-state {
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 300px;
}

.empty-card {
	background: rgba(255, 255, 255, 0.8);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	max-width: 500px;
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
