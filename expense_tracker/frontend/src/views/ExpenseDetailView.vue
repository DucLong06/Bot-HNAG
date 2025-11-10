<template>
	<div v-if="expense" class="expense-detail-page">
		<!-- Back Button -->
		<div class="back-section mb-6">
			<v-btn
				@click="$router.go(-1)"
				variant="outlined"
				rounded="xl"
				class="back-btn"
			>
				<v-icon size="18" class="mr-2">mdi-arrow-left</v-icon>
				Quay lại
			</v-btn>
		</div>

		<!-- Page Header -->
		<div class="detail-header mb-8">
			<v-card class="header-card pa-8" rounded="xl" elevation="0">
				<div class="header-content">
					<div class="header-icon">
						<v-icon size="48" color="white">mdi-receipt</v-icon>
					</div>
					<div class="header-text">
						<h1 class="expense-name text-3xl font-bold mb-2">
							{{ expense.name }}
						</h1>
						<div class="expense-amount-container">
							<div class="expense-amount text-4xl font-bold mb-4">
								{{ formatCurrency(expense.total_amount) }}
							</div>
						</div>
						<div class="expense-meta d-flex align-center flex-wrap">
							<v-chip
								color="success"
								rounded="lg"
								class="mr-3 mb-2 meta-chip"
							>
								<v-icon size="16" class="mr-1"
									>mdi-account-cash</v-icon
								>
								{{ expense.payer.name }}
							</v-chip>
							<v-chip
								color="info"
								rounded="lg"
								class="mr-3 mb-2 meta-chip"
							>
								<v-icon size="16" class="mr-1"
									>mdi-account-group</v-icon
								>
								{{ expense.participants.length }} người
							</v-chip>
							<v-chip
								color="orange"
								rounded="lg"
								class="mb-2 meta-chip"
							>
								<v-icon size="16" class="mr-1"
									>mdi-calendar</v-icon
								>
								{{ formatDate(expense.created_at) }}
							</v-chip>
						</div>
					</div>
				</div>
			</v-card>
		</div>

		<!-- Main Content -->
		<v-row>
			<!-- Left Column - Participants -->
			<v-col cols="12" lg="8">
				<v-card class="participants-card" rounded="xl" elevation="0">
					<div class="card-header pa-6 pb-0">
						<h2
							class="card-title text-xl font-bold d-flex align-center"
						>
							<v-icon class="mr-3" color="primary"
								>mdi-account-multiple</v-icon
							>
							Danh sách người tham gia
						</h2>
					</div>

					<v-card-text class="pa-6 pt-4">
						<div class="participants-grid">
							<div
								v-for="participant in expense.participants"
								:key="participant.id"
								class="participant-card"
							>
								<v-card
									class="participant-item pa-4"
									rounded="lg"
									elevation="0"
									:class="{
										paid: participant.is_paid,
										unpaid: !participant.is_paid,
									}"
								>
									<div
										class="participant-header d-flex align-center justify-space-between mb-3"
									>
										<div
											class="participant-info d-flex align-center"
										>
											<v-avatar
												:color="
													participant.is_paid
														? 'success'
														: 'error'
												"
												class="mr-3"
												size="40"
											>
												<span
													class="text-white font-weight-bold"
												>
													{{
														participant.member.name
															.charAt(0)
															.toUpperCase()
													}}
												</span>
											</v-avatar>
											<div>
												<div
													class="participant-name font-weight-bold"
												>
													{{
														participant.member.name
													}}
												</div>
												<div
													class="participant-amount text-lg font-bold text-primary"
												>
													{{
														formatCurrency(
															participant.amount_owed
														)
													}}
												</div>
											</div>
										</div>

										<div class="participant-actions">
											<v-chip
												:color="
													participant.is_paid
														? 'success'
														: 'error'
												"
												rounded="lg"
												class="status-chip"
											>
												<v-icon size="14" class="mr-1">
													{{
														participant.is_paid
															? "mdi-check-circle"
															: "mdi-clock-outline"
													}}
												</v-icon>
												{{
													participant.is_paid
														? "Đã trả"
														: "Chưa trả"
												}}
											</v-chip>
										</div>
									</div>

									<!-- Payer Info -->
									<div
										v-if="
											expense.payer.id ===
											participant.member.id
										"
										class="payer-info mb-3"
									>
										<v-alert
											type="info"
											variant="tonal"
											rounded="lg"
											density="compact"
										>
											<template v-slot:prepend>
												<v-icon size="16"
													>mdi-account-cash</v-icon
												>
											</template>
											<div class="text-sm">
												<div class="font-weight-medium">
													Người trả tiền
												</div>
												<div
													v-if="
														participant.member
															.bank_name
													"
													class="mt-1"
												>
													🏦
													{{
														participant.member
															.bank_name
													}}
												</div>
												<div
													v-if="
														participant.member
															.account_number
													"
													class="mt-1"
												>
													💳
													{{
														participant.member
															.account_number
													}}
												</div>
											</div>
										</v-alert>
									</div>

									<!-- Action Button -->
									<div
										v-if="authStore.isAuthenticated"
										class="participant-action"
									>
										<v-btn
											@click="togglePaid(participant)"
											:color="
												participant.is_paid
													? 'error'
													: 'success'
											"
											variant="elevated"
											block
											rounded="lg"
											class="action-toggle"
										>
											<v-icon size="18" class="mr-2">
												{{
													participant.is_paid
														? "mdi-close-circle"
														: "mdi-check-circle"
												}}
											</v-icon>
											{{
												participant.is_paid
													? "Đánh dấu chưa trả"
													: "Đánh dấu đã trả"
											}}
										</v-btn>
									</div>
								</v-card>
							</div>
						</div>
					</v-card-text>
				</v-card>
			</v-col>

			<!-- Right Column - Stats & Actions -->
			<v-col cols="12" lg="4">
				<!-- Statistics Card -->
				<v-card class="stats-card mb-6" rounded="xl" elevation="0">
					<div class="card-header pa-6 pb-0">
						<h3
							class="card-title text-lg font-bold d-flex align-center"
						>
							<v-icon class="mr-3" color="primary"
								>mdi-chart-line</v-icon
							>
							Thống kê thanh toán
						</h3>
					</div>

					<v-card-text class="pa-6 pt-4">
						<div class="stats-grid">
							<div class="stat-item">
								<div class="stat-icon success">
									<v-icon color="white" size="20"
										>mdi-check-circle</v-icon
									>
								</div>
								<div class="stat-content">
									<div
										class="stat-number text-2xl font-bold text-success"
									>
										{{ paidCount }}
									</div>
									<div class="stat-label">Đã thanh toán</div>
								</div>
							</div>

							<div class="stat-item">
								<div class="stat-icon error">
									<v-icon color="white" size="20"
										>mdi-clock-outline</v-icon
									>
								</div>
								<div class="stat-content">
									<div
										class="stat-number text-2xl font-bold text-error"
									>
										{{ unpaidCount }}
									</div>
									<div class="stat-label">
										Chưa thanh toán
									</div>
								</div>
							</div>

							<div class="stat-item">
								<div class="stat-icon success">
									<v-icon color="white" size="20"
										>mdi-currency-usd</v-icon
									>
								</div>
								<div class="stat-content">
									<div
										class="stat-number text-lg font-bold text-success"
									>
										{{ formatCurrency(paidAmount) }}
									</div>
									<div class="stat-label">Đã thu được</div>
								</div>
							</div>

							<div class="stat-item">
								<div class="stat-icon error">
									<v-icon color="white" size="20"
										>mdi-currency-usd</v-icon
									>
								</div>
								<div class="stat-content">
									<div
										class="stat-number text-lg font-bold text-error"
									>
										{{ formatCurrency(unpaidAmount) }}
									</div>
									<div class="stat-label">Còn thiếu</div>
								</div>
							</div>
						</div>

						<!-- Progress Bar -->
						<div class="progress-section mt-6">
							<div
								class="d-flex justify-space-between align-center mb-2"
							>
								<span class="text-sm font-weight-medium"
									>Tiến độ</span
								>
								<span class="text-sm font-weight-bold"
									>{{
										Math.round(
											(paidCount /
												expense.participants.length) *
												100
										)
									}}%</span
								>
							</div>
							<v-progress-linear
								:model-value="
									(paidCount / expense.participants.length) *
									100
								"
								color="success"
								height="8"
								rounded
								class="progress-bar"
							></v-progress-linear>
						</div>
					</v-card-text>
				</v-card>

				<!-- Telegram Reminders Card -->
				<v-card
					v-if="
						authStore.isAuthenticated &&
						unpaidParticipants.length > 0
					"
					class="reminders-card"
					rounded="xl"
					elevation="0"
				>
					<div class="card-header pa-6 pb-0">
						<h3
							class="card-title text-lg font-bold d-flex align-center"
						>
							<v-icon class="mr-3" color="primary"
								>mdi-telegram</v-icon
							>
							Gửi nhắc nhở
						</h3>
					</div>

					<v-card-text class="pa-6 pt-4">
						<!-- Individual Reminders -->
						<div class="individual-reminders mb-4">
							<p class="text-sm text-on-surface-variant mb-3">
								Nhắc nhở từng người:
							</p>
							<div class="reminder-buttons">
								<v-btn
									v-for="participant in unpaidParticipants"
									:key="participant.id"
									@click="
										sendReminder(
											participant.member.id,
											participant.id
										)
									"
									color="orange"
									variant="outlined"
									size="small"
									rounded="lg"
									:loading="loadingStates[participant.id]"
									class="reminder-btn mb-2 mr-2"
									block
								>
									<v-icon size="16" class="mr-2"
										>mdi-send</v-icon
									>
									{{ participant.member.name }}
								</v-btn>
							</div>
						</div>

						<!-- Bulk Reminder -->
						<v-divider class="mb-4"></v-divider>
						<div class="bulk-reminder">
							<p class="text-sm text-on-surface-variant mb-3">
								Gửi cho tất cả:
							</p>
							<v-btn
								@click="sendBulkReminders"
								color="error"
								variant="elevated"
								:loading="loading"
								block
								rounded="lg"
								class="bulk-btn"
							>
								<v-icon size="18" class="mr-2"
									>mdi-send-outline</v-icon
								>
								Nhắc nhở {{ unpaidParticipants.length }} người
							</v-btn>
						</div>
					</v-card-text>
				</v-card>
			</v-col>
		</v-row>

		<!-- Success Snackbar -->
		<v-snackbar
			v-model="snackbar.show"
			:color="snackbar.color"
			timeout="3000"
			rounded="lg"
			class="modern-snackbar"
		>
			<div class="d-flex align-center">
				<v-icon class="mr-3">{{ snackbar.icon }}</v-icon>
				{{ snackbar.text }}
			</div>
			<template v-slot:actions>
				<v-btn
					color="white"
					variant="text"
					@click="snackbar.show = false"
					size="small"
					rounded="lg"
				>
					Đóng
				</v-btn>
			</template>
		</v-snackbar>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { expensesApi, telegramApi } from "../services/api";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const authStore = useAuthStore();
const expense = ref(null);
const loading = ref(false);
const loadingStates = ref({});

// Snackbar for notifications
const snackbar = reactive({
	show: false,
	text: "",
	color: "success",
	icon: "mdi-check-circle",
});

const unpaidParticipants = computed(() => {
	if (!expense.value) return [];
	return expense.value.participants.filter((p: any) => !p.is_paid);
});

const paidCount = computed(() => {
	if (!expense.value) return 0;
	return expense.value.participants.filter((p: any) => p.is_paid).length;
});

const unpaidCount = computed(() => {
	if (!expense.value) return 0;
	return expense.value.participants.filter((p: any) => !p.is_paid).length;
});

const paidAmount = computed(() => {
	if (!expense.value) return 0;
	return expense.value.participants
		.filter((p: any) => p.is_paid)
		.reduce((sum: number, p: any) => sum + p.amount_owed, 0);
});

const unpaidAmount = computed(() => {
	if (!expense.value) return 0;
	return expense.value.participants
		.filter((p: any) => !p.is_paid)
		.reduce((sum: number, p: any) => sum + p.amount_owed, 0);
});

// Show notification function
const showNotification = (
	text: string,
	color: string = "success",
	icon: string = "mdi-check-circle"
) => {
	snackbar.text = text;
	snackbar.color = color;
	snackbar.icon = icon;
	snackbar.show = true;
};

const fetchExpense = async () => {
	try {
		const response = await expensesApi.get(Number(route.params.id));
		expense.value = response.data;
	} catch (error) {
		console.error("Error fetching expense:", error);
		showNotification(
			"Có lỗi khi tải chi tiết khoản chi tiêu",
			"error",
			"mdi-alert-circle"
		);
	}
};

const togglePaid = async (participant: any) => {
	try {
		await expensesApi.markPaid(expense.value.id, participant.member.id);
		participant.is_paid = !participant.is_paid;

		showNotification(
			`Đã cập nhật trạng thái thanh toán cho ${participant.member.name}`
		);
	} catch (error) {
		console.error("Error marking paid:", error);
		showNotification(
			"Có lỗi khi cập nhật trạng thái",
			"error",
			"mdi-alert-circle"
		);
	}
};

const sendReminder = async (memberId: number, participantId: number) => {
	console.log("=== SENDING SINGLE REMINDER ===");
	console.log("Member ID:", memberId);
	console.log("Participant ID:", participantId);

	// Set loading cho button cụ thể
	loadingStates.value[participantId] = true;

	try {
		const response = await telegramApi.sendReminder(memberId);
		console.log("API Response:", response.data);

		const participant = unpaidParticipants.value.find(
			(p) => p.id === participantId
		);
		showNotification(`Đã gửi nhắc nhở cho ${participant?.member.name}!`);
	} catch (error: any) {
		console.error("Error sending reminder:", error);
		console.error("Error details:", error.response?.data);
		showNotification(
			"Có lỗi khi gửi nhắc nhở",
			"error",
			"mdi-alert-circle"
		);
	} finally {
		// Clear loading cho button cụ thể
		loadingStates.value[participantId] = false;
	}
};

const sendBulkReminders = async () => {
	console.log("=== SENDING BULK REMINDERS ===");
	const memberIds = unpaidParticipants.value.map((p: any) => p.member.id);
	console.log("Member IDs:", memberIds);

	loading.value = true; // Dùng loading chung cho bulk
	try {
		const response = await telegramApi.sendBulkReminders(memberIds);
		console.log("Bulk API Response:", response.data);

		showNotification(`Đã gửi nhắc nhở cho ${memberIds.length} người!`);
	} catch (error: any) {
		console.error("Error sending bulk reminders:", error);
		showNotification(
			"Có lỗi khi gửi nhắc nhở hàng loạt",
			"error",
			"mdi-alert-circle"
		);
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

const formatDate = (dateString: string) => {
	return new Date(dateString).toLocaleDateString("vi-VN", {
		year: "numeric",
		month: "long",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	});
};

onMounted(fetchExpense);
</script>

<style scoped>
.expense-detail-page {
	max-width: 1200px;
	margin: 0 auto;
	animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(20px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.back-btn {
	font-weight: 500;
	text-transform: none;
}

.back-btn:hover {
	transform: translateX(-2px);
}

.header-card {
	background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
	color: white;
	border: 1px solid rgba(79, 70, 229, 0.2);
	position: relative;
	overflow: hidden;
}

.header-card::before {
	content: "";
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: linear-gradient(
		135deg,
		rgba(0, 0, 0, 0.1) 0%,
		rgba(0, 0, 0, 0.3) 100%
	);
	z-index: 1;
}

.header-content {
	display: flex;
	align-items: center;
	gap: 2rem;
	position: relative;
	z-index: 2;
}

.header-icon {
	width: 80px;
	height: 80px;
	border-radius: 20px;
	background: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
	backdrop-filter: blur(10px);
	border: 2px solid rgba(255, 255, 255, 0.3);
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.expense-name {
	color: #ffffff;
	line-height: 1.2;
	text-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
	font-weight: 700;
	word-break: break-word;
	filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.expense-amount-container {
	background: rgba(255, 255, 255, 0.15);
	border-radius: 16px;
	padding: 12px 20px;
	border: 2px solid rgba(255, 255, 255, 0.25);
	backdrop-filter: blur(10px);
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	display: inline-block;
	margin-bottom: 1rem;
}

.expense-amount {
	color: #ffffff;
	text-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
	font-weight: 800;
	word-break: break-word;
	filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
	margin-bottom: 0 !important;
}

.expense-meta .meta-chip {
	background: rgba(255, 255, 255, 0.95) !important;
	color: rgb(55, 65, 81) !important;
	font-weight: 600;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
	border: 1px solid rgba(255, 255, 255, 0.5);
	backdrop-filter: blur(8px);
}

.participants-card,
.stats-card,
.reminders-card {
	background: rgba(255, 255, 255, 0.98);
	backdrop-filter: blur(20px);
	border: 1px solid rgba(79, 70, 229, 0.1);
	box-shadow: 0 8px 32px rgba(79, 70, 229, 0.1);
}

.card-header {
	border-bottom: 1px solid rgba(79, 70, 229, 0.1);
}

.card-title {
	color: rgb(31, 41, 55);
	font-weight: 600;
}

.participants-grid {
	display: grid;
	gap: 1rem;
	margin-top: 1rem;
}

.participant-item {
	border: 2px solid transparent;
	transition: all 0.3s ease;
	background: rgba(248, 250, 252, 0.9);
	backdrop-filter: blur(10px);
}

.participant-item.paid {
	border-color: rgba(34, 197, 94, 0.4);
	background: rgba(34, 197, 94, 0.08);
}

.participant-item.unpaid {
	border-color: rgba(239, 68, 68, 0.4);
	background: rgba(239, 68, 68, 0.08);
}

.participant-item:hover {
	transform: translateY(-4px);
	box-shadow: 0 16px 48px rgba(79, 70, 229, 0.15);
}

.participant-name {
	color: rgb(31, 41, 55);
	font-size: 1rem;
	font-weight: 600;
}

.participant-amount {
	margin-top: 0.25rem;
	font-weight: 700;
	word-break: break-word;
}

.status-chip {
	font-weight: 500;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-toggle {
	font-weight: 500;
	text-transform: none;
	transition: all 0.3s ease;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-toggle:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stats-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1rem;
	margin-bottom: 1rem;
}

.stat-item {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	padding: 1rem;
	border-radius: 12px;
	background: rgba(248, 250, 252, 0.9);
	border: 1px solid rgba(79, 70, 229, 0.1);
	transition: all 0.3s ease;
	backdrop-filter: blur(10px);
}

.stat-item:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 24px rgba(79, 70, 229, 0.1);
}

.stat-icon {
	width: 36px;
	height: 36px;
	border-radius: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.stat-icon.success {
	background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
	box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.stat-icon.error {
	background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
	box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.stat-content {
	flex: 1;
	min-width: 0;
}

.stat-number {
	line-height: 1.2;
	margin-bottom: 0.25rem;
	font-weight: 700;
	word-break: break-word;
}

.stat-label {
	color: rgb(107, 114, 128);
	font-size: 0.75rem;
	font-weight: 500;
	line-height: 1;
}

.progress-section {
	padding: 1.25rem;
	border-radius: 12px;
	background: rgba(248, 250, 252, 0.9);
	border: 1px solid rgba(79, 70, 229, 0.1);
	backdrop-filter: blur(10px);
}

.progress-bar {
	border-radius: 6px;
	background: rgba(226, 232, 240, 0.8);
	overflow: hidden;
	margin-top: 0.5rem;
}

.progress-bar :deep(.v-progress-linear__background) {
	background: rgba(226, 232, 240, 0.6);
}

.progress-bar :deep(.v-progress-linear__determinate) {
	background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
	transition: width 0.3s ease;
}

.reminder-buttons {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
	margin-top: 0.5rem;
}

.reminder-btn {
	font-weight: 500;
	text-transform: none;
	justify-content: flex-start;
	transition: all 0.3s ease;
}

.reminder-btn:hover:not(:disabled) {
	transform: translateY(-1px);
	box-shadow: 0 6px 16px rgba(255, 152, 0, 0.2);
}

.bulk-btn {
	font-weight: 600;
	text-transform: none;
	transition: all 0.3s ease;
}

.bulk-btn:hover:not(:disabled) {
	transform: translateY(-1px);
	box-shadow: 0 6px 20px rgba(239, 68, 68, 0.3);
}

.modern-snackbar {
	backdrop-filter: blur(10px);
	border-radius: 12px;
	font-family: "Inter", sans-serif;
}

/* Cross-browser compatibility */
.expense-detail-page {
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
}

.expense-detail-page .v-btn,
.expense-detail-page .v-chip,
.expense-detail-page .v-card {
	-webkit-font-smoothing: antialiased;
}

/* Animation performance */
.expense-detail-page .participant-item,
.expense-detail-page .stat-item,
.expense-detail-page .v-btn {
	transform: translateZ(0);
	backface-visibility: hidden;
}

/* Focus improvements */
.expense-detail-page .v-btn:focus-visible {
	outline: 2px solid rgba(79, 70, 229, 0.5);
	outline-offset: 2px;
}

/* Print styles */
@media print {
	.expense-detail-page .back-btn,
	.expense-detail-page .reminders-card,
	.expense-detail-page .action-toggle {
		display: none !important;
	}

	.expense-detail-page {
		max-width: none;
		margin: 0;
	}
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
	.expense-detail-page *,
	.expense-detail-page *::before,
	.expense-detail-page *::after {
		animation-duration: 0.01ms !important;
		animation-iteration-count: 1 !important;
		transition-duration: 0.01ms !important;
	}
}

/* High contrast support */
@media (prefers-contrast: high) {
	.expense-detail-page .participants-card,
	.expense-detail-page .stats-card,
	.expense-detail-page .reminders-card {
		border: 2px solid #000;
	}

	.expense-detail-page .participant-item {
		border: 2px solid #000;
	}

	.expense-detail-page .stat-item {
		border: 2px solid #000;
	}
}

/* Zoom support */
@media (min-resolution: 2dppx) {
	.expense-detail-page .v-icon {
		image-rendering: -webkit-optimize-contrast;
		image-rendering: crisp-edges;
	}
}

/* Orientation support */
@media (orientation: landscape) and (max-height: 600px) {
	.expense-detail-page .header-card {
		padding: 1.5rem;
	}

	.expense-detail-page .expense-name {
		font-size: 1.5rem;
	}

	.expense-detail-page .expense-amount {
		font-size: 1.75rem;
	}
}

/* Additional dark mode enhancements */
.v-theme--dark .expense-detail-page .expense-meta .meta-chip {
	background: rgba(51, 65, 85, 0.95) !important;
	color: rgb(203, 213, 225) !important;
}

.v-theme--dark
	.expense-detail-page
	.progress-bar
	:deep(.v-progress-linear__background) {
	background: rgba(51, 65, 85, 0.6);
}

/* Final enhancements */
.expense-detail-page .v-card:not(.header-card) {
	background: rgba(255, 255, 255, 0.98) !important;
	border: 1px solid rgba(79, 70, 229, 0.1) !important;
}

.v-theme--dark .expense-detail-page .v-card:not(.header-card) {
	background: rgba(30, 41, 59, 0.98) !important;
	border: 1px solid rgba(129, 140, 248, 0.2) !important;
}

/* Final touches */
.expense-detail-page {
	scroll-behavior: smooth;
}

.expense-detail-page .v-main {
	scroll-behavior: smooth;
}

/* Sticky positioning support */
.expense-detail-page .back-section {
	position: sticky;
	top: 0;
	z-index: 10;
	background: rgba(248, 250, 252, 0.95);
	backdrop-filter: blur(20px);
	padding: 1rem 0;
	margin-bottom: 1rem;
}

/* Overflow handling */
.expense-detail-page .participant-name,
.expense-detail-page .stat-number,
.expense-detail-page .expense-name,
.expense-detail-page .expense-amount {
	overflow-wrap: break-word;
	word-wrap: break-word;
	hyphens: auto;
}

/* Final consistency check */
.expense-detail-page .v-btn:not(:disabled):hover {
	transform: translateY(-1px);
	box-shadow: 0 6px 20px rgba(79, 70, 229, 0.15);
}

.expense-detail-page .v-chip:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
}

/* Box shadow optimization */
.expense-detail-page .v-card,
.expense-detail-page .v-btn,
.expense-detail-page .v-chip {
	box-shadow: 0 4px 12px rgba(79, 70, 229, 0.08);
}

.expense-detail-page .v-card:hover,
.expense-detail-page .participant-item:hover {
	box-shadow: 0 12px 48px rgba(79, 70, 229, 0.15);
}

/* Backdrop filter optimization */
.expense-detail-page .v-card,
.expense-detail-page .modern-snackbar {
	backdrop-filter: blur(20px);
	-webkit-backdrop-filter: blur(20px);
}

/* Final optimization */
.expense-detail-page {
	contain: layout style;
}

/* State-specific enhancements */
.expense-detail-page .v-btn:active {
	transform: translateY(0);
}

.expense-detail-page .v-chip:active {
	transform: translateY(0);
}

.expense-detail-page .participant-item:active {
	transform: translateY(0);
}

/* Loading state improvements */
.expense-detail-page .v-btn[loading] {
	opacity: 0.8;
	cursor: not-allowed;
	transform: none;
}

.expense-detail-page .v-progress-linear {
	border-radius: 6px;
	overflow: hidden;
}

/* Disabled state improvements */
.expense-detail-page .v-btn:disabled {
	opacity: 0.5;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.expense-detail-page .v-btn:disabled:hover {
	transform: none;
	box-shadow: none;
}

/* Error state improvements */
.expense-detail-page .v-alert {
	border-radius: 12px;
	font-family: "Inter", sans-serif;
}

.expense-detail-page .v-alert--error {
	background: rgba(239, 68, 68, 0.1);
	border: 1px solid rgba(239, 68, 68, 0.3);
}

.expense-detail-page .v-alert--success {
	background: rgba(34, 197, 94, 0.1);
	border: 1px solid rgba(34, 197, 94, 0.3);
}

.expense-detail-page .v-alert--info {
	background: rgba(59, 130, 246, 0.1);
	border: 1px solid rgba(59, 130, 246, 0.3);
}

.expense-detail-page .v-alert--warning {
	background: rgba(245, 158, 11, 0.1);
	border: 1px solid rgba(245, 158, 11, 0.3);
}

/* Success state improvements */
.expense-detail-page .v-btn--success {
	background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
	box-shadow: 0 6px 20px rgba(34, 197, 94, 0.3);
}

.expense-detail-page .v-btn--error {
	background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
	box-shadow: 0 6px 20px rgba(239, 68, 68, 0.3);
}

.expense-detail-page .v-chip--success {
	background: rgba(34, 197, 94, 0.15);
	color: #15803d;
}

.expense-detail-page .v-chip--error {
	background: rgba(239, 68, 68, 0.15);
	color: #dc2626;
}

/* Avatar improvements */
.expense-detail-page .v-avatar {
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	border: 2px solid rgba(255, 255, 255, 0.8);
}

/* Divider improvements */
.expense-detail-page .v-divider {
	border-color: rgba(79, 70, 229, 0.1);
	opacity: 0.6;
}

.v-theme--dark .expense-detail-page .v-divider {
	border-color: rgba(129, 140, 248, 0.2);
}

/* Selection improvements */
.expense-detail-page ::selection {
	background: rgba(79, 70, 229, 0.2);
	color: inherit;
}

.expense-detail-page ::-moz-selection {
	background: rgba(79, 70, 229, 0.2);
	color: inherit;
}

/* Transform improvements */
.expense-detail-page .v-btn,
.expense-detail-page .v-chip,
.expense-detail-page .v-card,
.expense-detail-page .participant-item {
	transform-origin: center center;
	transform-style: preserve-3d;
}

/* Final polish touches */
.expense-detail-page {
	background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
	min-height: 100vh;
	position: relative;
}

.expense-detail-page::before {
	content: "";
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%234f46e5' fill-opacity='0.02'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")
		repeat;
	pointer-events: none;
	z-index: 0;
}

.expense-detail-page > * {
	position: relative;
	z-index: 1;
}

@media (max-width: 768px) {
	.header-content {
		flex-direction: column;
		text-align: center;
		gap: 1rem;
	}

	.header-icon {
		width: 60px;
		height: 60px;
	}

	.expense-name {
		font-size: 1.75rem;
	}

	.expense-amount {
		font-size: 2rem;
	}

	.stats-grid {
		grid-template-columns: 1fr;
		gap: 1rem;
	}

	.stat-item {
		padding: 0.75rem;
	}

	.expense-amount-container {
		padding: 10px 16px;
	}
}

@media (max-width: 600px) {
	.participants-grid {
		gap: 0.75rem;
	}

	.participant-item {
		padding: 1rem;
	}

	.participant-header {
		flex-direction: column;
		align-items: flex-start;
		gap: 0.75rem;
	}

	.participant-actions {
		align-self: stretch;
	}

	.expense-meta {
		justify-content: center;
	}

	.reminder-btn {
		margin-bottom: 0.5rem;
		word-break: break-word;
	}

	.bulk-btn {
		word-break: break-word;
	}

	.expense-meta .meta-chip {
		margin: 0.25rem 0.5rem !important;
	}
}

/* Animation for cards */
.participant-card {
	animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
	from {
		opacity: 0;
		transform: translateY(20px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

/* Loading states */
.reminder-btn:disabled {
	opacity: 0.7;
}

.bulk-btn:disabled {
	opacity: 0.7;
}

/* Success pulse animation for paid items */
.participant-item.paid {
	animation: successPulse 0.5s ease-out;
}

@keyframes successPulse {
	0% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.02);
	}
	100% {
		transform: scale(1);
	}
}

.payer-info {
	margin-bottom: 1rem;
}

.payer-info .v-alert {
	border: 1px solid rgba(59, 130, 246, 0.3);
	box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.individual-reminders {
	margin-bottom: 1.5rem;
}

.individual-reminders p {
	margin-bottom: 0.75rem;
	font-weight: 500;
	color: rgb(107, 114, 128);
}

.bulk-reminder p {
	margin-bottom: 0.75rem;
	font-weight: 500;
	color: rgb(107, 114, 128);
}

/* Custom scrollbar if needed */
.participants-grid::-webkit-scrollbar {
	width: 6px;
}

.participants-grid::-webkit-scrollbar-thumb {
	background: rgba(79, 70, 229, 0.3);
	border-radius: 3px;
}
</style>
