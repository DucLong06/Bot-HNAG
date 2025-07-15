<template>
	<div class="home-page">
		<!-- Hero Section -->
		<div class="hero-section text-center mb-12">
			<div class="hero-content">
				<div class="hero-icon mb-6">
					<div class="icon-wrapper">
						<v-icon size="64" class="hero-main-icon"
							>mdi-calculator-variant</v-icon
						>
						<div class="icon-glow"></div>
					</div>
				</div>
				<h1 class="hero-title text-5xl font-bold mb-4">
					Danh sách chi tiêu
				</h1>
				<p class="hero-subtitle text-xl mb-6">
					Quản lý chi tiêu nhóm một cách thông minh và hiệu quả
				</p>

				<!-- Quick Stats -->
				<div v-if="expenses.length > 0" class="quick-stats mb-8">
					<v-row justify="center">
						<v-col cols="auto">
							<v-card
								class="stats-card pa-4 mx-2"
								rounded="xl"
								elevation="0"
							>
								<div
									class="stats-number text-2xl font-bold text-primary"
								>
									{{ expenses.length }}
								</div>
								<div class="stats-label text-sm">
									Khoản chi tiêu
								</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card
								class="stats-card pa-4 mx-2"
								rounded="xl"
								elevation="0"
							>
								<div
									class="stats-number text-2xl font-bold text-success"
								>
									{{ totalPaid }}
								</div>
								<div class="stats-label text-sm">
									Đã thanh toán
								</div>
							</v-card>
						</v-col>
						<v-col cols="auto">
							<v-card
								class="stats-card pa-4 mx-2"
								rounded="xl"
								elevation="0"
							>
								<div
									class="stats-number text-2xl font-bold text-error"
								>
									{{ totalUnpaid }}
								</div>
								<div class="stats-label text-sm">
									Chưa thanh toán
								</div>
							</v-card>
						</v-col>
					</v-row>
				</div>
			</div>
		</div>

		<!-- Expenses Grid -->
		<div v-if="expenses.length > 0">
			<div class="section-header mb-6">
				<h2 class="text-2xl font-bold text-gray-800">
					Các khoản chi tiêu gần đây
				</h2>
				<p class="text-gray-600 mt-1">
					Theo dõi và quản lý chi tiêu của bạn
				</p>
			</div>

			<v-row>
				<v-col
					v-for="(expense, index) in expenses"
					:key="expense.id"
					cols="12"
					md="6"
					lg="4"
				>
					<v-card
						class="expense-card h-100"
						rounded="xl"
						elevation="0"
						:style="`animation-delay: ${index * 100}ms`"
						@click="navigateToDetail(expense.id)"
					>
						<!-- Card Header -->
						<div class="card-header pa-6 pb-0">
							<div
								class="d-flex align-center justify-space-between mb-4"
							>
								<div class="expense-icon">
									<v-icon size="24" color="white"
										>mdi-receipt</v-icon
									>
								</div>
								<div class="expense-status">
									<v-chip
										:color="getStatusColor(expense)"
										size="small"
										rounded="lg"
									>
										{{ getStatusText(expense) }}
									</v-chip>
								</div>
							</div>
							<h3 class="expense-title text-xl font-bold mb-2">
								{{ expense.name }}
							</h3>
							<div class="expense-amount text-2xl font-bold mb-4">
								{{ formatCurrency(expense.total_amount) }}
							</div>
						</div>

						<!-- Card Content -->
						<v-card-text class="pa-6 pt-0">
							<div class="expense-details space-y-3">
								<div class="detail-item d-flex align-center">
									<v-icon
										size="18"
										color="success"
										class="mr-3"
										>mdi-account-cash</v-icon
									>
									<span class="detail-label">Người trả:</span>
									<span
										class="detail-value ml-auto font-medium"
										>{{ expense.payer.name }}</span
									>
								</div>

								<div class="detail-item d-flex align-center">
									<v-icon
										size="18"
										color="orange"
										class="mr-3"
										>mdi-account-group</v-icon
									>
									<span class="detail-label">Số người:</span>
									<span
										class="detail-value ml-auto font-medium"
										>{{ expense.participants.length }}</span
									>
								</div>

								<div class="detail-item d-flex align-center">
									<v-icon
										size="18"
										color="purple"
										class="mr-3"
										>mdi-calendar</v-icon
									>
									<span class="detail-label">Ngày tạo:</span>
									<span
										class="detail-value ml-auto font-medium"
										>{{
											formatDate(expense.created_at)
										}}</span
									>
								</div>
							</div>

							<v-divider class="my-4"></v-divider>

							<!-- Participants Status -->
							<div class="participants-section">
								<h4
									class="participants-title font-medium mb-3 d-flex align-center"
								>
									<v-icon size="16" class="mr-2"
										>mdi-chart-pie</v-icon
									>
									Trạng thái thanh toán
								</h4>
								<div class="participants-grid">
									<v-chip
										v-for="participant in expense.participants.slice(
											0,
											6
										)"
										:key="participant.id"
										:color="
											participant.is_paid
												? 'success'
												: 'error'
										"
										size="small"
										rounded="lg"
										class="ma-1"
									>
										<v-icon size="12" class="mr-1">
											{{
												participant.is_paid
													? "mdi-check-circle"
													: "mdi-clock-outline"
											}}
										</v-icon>
										{{ participant.member.name }}
									</v-chip>
									<v-chip
										v-if="expense.participants.length > 6"
										color="surface-variant"
										size="small"
										rounded="lg"
										class="ma-1"
									>
										+{{ expense.participants.length - 6 }}
									</v-chip>
								</div>
							</div>
						</v-card-text>

						<!-- Card Actions -->
						<v-card-actions class="pa-6 pt-0">
							<v-btn
								:to="`/expenses/${expense.id}`"
								color="primary"
								variant="elevated"
								rounded="lg"
								block
								class="action-btn"
							>
								<v-icon size="18" class="mr-2">mdi-eye</v-icon>
								Xem chi tiết
							</v-btn>
						</v-card-actions>
					</v-card>
				</v-col>
			</v-row>
		</div>

		<!-- Empty State -->
		<div v-else class="empty-state">
			<v-card
				class="empty-card text-center pa-12"
				rounded="xl"
				elevation="0"
			>
				<div class="empty-icon mb-6">
					<v-icon size="96" color="surface-variant"
						>mdi-receipt-text-outline</v-icon
					>
					<div class="empty-decoration"></div>
				</div>
				<h3 class="empty-title text-2xl font-bold mb-4">
					Chưa có khoản chi tiêu nào
				</h3>
				<p class="empty-subtitle text-lg text-on-surface-variant mb-8">
					Hãy tạo khoản chi tiêu đầu tiên để bắt đầu quản lý tài chính
					nhóm
				</p>
				<v-btn
					v-if="authStore.isAuthenticated"
					to="/expenses"
					color="primary"
					variant="elevated"
					size="large"
					rounded="xl"
					class="px-8 py-2"
				>
					<v-icon size="20" class="mr-2">mdi-plus</v-icon>
					Tạo chi tiêu đầu tiên
				</v-btn>
			</v-card>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { expensesApi } from "../services/api";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const expenses = ref([]);

const totalPaid = computed(() => {
	return expenses.value.reduce((total, expense) => {
		return total + expense.participants.filter((p) => p.is_paid).length;
	}, 0);
});

const totalUnpaid = computed(() => {
	return expenses.value.reduce((total, expense) => {
		return total + expense.participants.filter((p) => !p.is_paid).length;
	}, 0);
});

const fetchExpenses = async () => {
	try {
		const response = await expensesApi.getAll();
		expenses.value = response.data;
	} catch (error) {
		console.error("Error fetching expenses:", error);
	}
};

const navigateToDetail = (expenseId) => {
	router.push(`/expenses/${expenseId}`);
};

const getStatusColor = (expense) => {
	const paidCount = expense.participants.filter((p) => p.is_paid).length;
	const totalCount = expense.participants.length;

	if (paidCount === totalCount) return "success";
	if (paidCount === 0) return "error";
	return "warning";
};

const getStatusText = (expense) => {
	const paidCount = expense.participants.filter((p) => p.is_paid).length;
	const totalCount = expense.participants.length;

	if (paidCount === totalCount) return "Hoàn thành";
	if (paidCount === 0) return "Chưa thanh toán";
	return `${paidCount}/${totalCount} đã trả`;
};

const formatCurrency = (amount: number) => {
	return new Intl.NumberFormat("vi-VN", {
		style: "currency",
		currency: "VND",
	}).format(amount);
};

const formatDate = (dateString: string) => {
	return new Date(dateString).toLocaleDateString("vi-VN");
};

onMounted(fetchExpenses);
</script>

<style scoped>
.home-page {
	max-width: 1200px;
	margin: 0 auto;
}

.hero-section {
	position: relative;
	padding: 4rem 0;
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
	background: radial-gradient(
		circle,
		rgba(102, 126, 234, 0.1) 0%,
		transparent 70%
	);
	border-radius: 50%;
	animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
	0%,
	100% {
		transform: translate(-50%, -50%) scale(1);
		opacity: 0.5;
	}
	50% {
		transform: translate(-50%, -50%) scale(1.1);
		opacity: 0.8;
	}
}

.hero-title {
	background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	line-height: 1.2;
}

.hero-subtitle {
	color: rgb(107, 114, 128);
}

.quick-stats {
	position: relative;
}

.stats-card {
	background: rgba(255, 255, 255, 0.8);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	transition: transform 0.2s ease;
	min-width: 120px;
}

.stats-card:hover {
	transform: translateY(-2px);
}

.stats-number {
	line-height: 1;
}

.stats-label {
	color: rgb(107, 114, 128);
	font-weight: 500;
}

.section-header {
	text-align: left;
}

.expense-card {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	transition: all 0.3s ease;
	cursor: pointer;
	animation: fadeInUp 0.6s ease forwards;
	opacity: 0;
	transform: translateY(20px);
}

@keyframes fadeInUp {
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.expense-card:hover {
	transform: translateY(-8px);
	box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
}

.card-header {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	border-radius: 16px 16px 0 0;
}

.expense-icon {
	width: 40px;
	height: 40px;
	border-radius: 10px;
	background: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
}

.expense-title {
	color: white;
	line-height: 1.3;
}

.expense-amount {
	color: rgba(255, 255, 255, 0.95);
}

.detail-item {
	padding: 0.5rem 0;
}

.detail-label {
	color: rgb(107, 114, 128);
	font-size: 0.875rem;
}

.detail-value {
	color: rgb(55, 65, 81);
	font-size: 0.875rem;
}

.participants-title {
	color: rgb(75, 85, 99);
	font-size: 0.875rem;
}

.participants-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 0.25rem;
	margin: -0.25rem;
}

.action-btn {
	font-weight: 500;
	text-transform: none;
}

.action-btn:hover {
	transform: translateY(-1px);
}

.empty-state {
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 400px;
}

.empty-card {
	background: rgba(255, 255, 255, 0.8);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	max-width: 500px;
	position: relative;
	overflow: hidden;
}

.empty-icon {
	position: relative;
	display: inline-block;
}

.empty-decoration {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	width: 150px;
	height: 150px;
	background: radial-gradient(
		circle,
		rgba(102, 126, 234, 0.05) 0%,
		transparent 70%
	);
	border-radius: 50%;
	animation: float 3s ease-in-out infinite;
}

@keyframes float {
	0%,
	100% {
		transform: translate(-50%, -50%) translateY(0px);
	}
	50% {
		transform: translate(-50%, -50%) translateY(-10px);
	}
}

.empty-title {
	color: rgb(31, 41, 55);
}

.empty-subtitle {
	max-width: 400px;
	margin: 0 auto;
}

@media (max-width: 768px) {
	.hero-title {
		font-size: 2.25rem;
	}

	.hero-subtitle {
		font-size: 1.125rem;
	}

	.quick-stats .v-col {
		flex: 1;
		max-width: none;
	}

	.stats-card {
		margin: 0.25rem !important;
	}
}

@media (max-width: 600px) {
	.hero-section {
		padding: 2rem 0;
	}

	.hero-title {
		font-size: 1.875rem;
	}

	.stats-card {
		min-width: 100px;
		padding: 0.75rem !important;
	}

	.stats-number {
		font-size: 1.5rem;
	}

	.empty-card {
		padding: 2rem 1.5rem !important;
	}
}
</style>
