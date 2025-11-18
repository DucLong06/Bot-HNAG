<template>
	<div class="expenses-page">
		<div class="page-header mb-8">
			<div class="header-content">
				<div class="header-text">
					<div class="header-icon-title">
						<div class="page-icon">
							<v-icon size="32" color="white"
								>mdi-credit-card</v-icon
							>
						</div>
						<div>
							<h1 class="page-title text-3xl font-bold">
								Quản lý chi tiêu
							</h1>
							<p class="page-subtitle">
								Tạo và quản lý các khoản chi tiêu nhóm
							</p>
						</div>
					</div>
				</div>
				<div class="header-actions">
					<v-btn
						color="primary"
						@click="openAddDialog"
						size="large"
						rounded="xl"
						class="add-btn"
					>
						<v-icon size="20" class="mr-2">mdi-plus</v-icon>
						Thêm khoản chi tiêu
					</v-btn>
				</div>
			</div>
		</div>

		<div class="filter-bar mb-6">
			<v-card class="pa-4 glass-effect" rounded="lg" elevation="0">
				<v-row align="center">
					<v-col cols="12" md="4">
						<v-text-field
							v-model="search"
							prepend-inner-icon="mdi-magnify"
							label="Tìm kiếm khoản chi..."
							variant="outlined"
							density="compact"
							hide-details
							rounded="lg"
							@update:model-value="handleSearch"
						></v-text-field>
					</v-col>
					<v-col cols="12" md="4">
						<v-select
							v-model="selectedPayer"
							:items="members"
							item-title="name"
							item-value="id"
							label="Lọc theo chủ nợ (Người trả)"
							prepend-inner-icon="mdi-account-cash"
							variant="outlined"
							density="compact"
							hide-details
							rounded="lg"
							clearable
							@update:model-value="handleFilter"
						></v-select>
					</v-col>
					<v-col cols="12" md="4" class="text-right">
						<v-chip
							v-if="expenses.length > 0"
							color="primary"
							variant="tonal"
						>
							Hiển thị {{ expenses.length }} khoản chi
						</v-chip>
					</v-col>
				</v-row>
			</v-card>
		</div>

		<div v-if="expenses.length > 0">
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
					>
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
									<v-icon size="18" color="info" class="mr-3"
										>mdi-account-edit</v-icon
									>
									<span class="detail-label">Người tạo:</span>
									<span
										class="detail-value ml-auto font-medium text-xs text-surface-variant"
									>
										{{
											expense.created_by_name || "Unknown"
										}}
									</span>
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
									>
										{{ formatDate(expense.created_at) }}
									</span>
								</div>
							</div>

							<v-divider class="my-4"></v-divider>

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

								<div
									v-if="!expense.is_owner"
									class="text-xs mt-3 text-warning d-flex align-center"
								>
									<v-icon size="14" class="mr-1"
										>mdi-lock-outline</v-icon
									>
									Chỉ người tạo mới có quyền chỉnh sửa
								</div>
							</div>
						</v-card-text>

						<v-card-actions class="pa-6 pt-0">
							<v-btn
								:to="`/expenses/${expense.id}`"
								color="primary"
								variant="outlined"
								size="small"
								rounded="lg"
								class="mr-2"
							>
								<v-icon size="16" class="mr-1">mdi-eye</v-icon>
								Chi tiết
							</v-btn>

							<template v-if="expense.is_owner">
								<v-btn
									@click="editExpense(expense)"
									color="orange"
									variant="outlined"
									size="small"
									rounded="lg"
									class="mr-2"
								>
									<v-icon size="16" class="mr-1"
										>mdi-pencil</v-icon
									>
									Sửa
								</v-btn>

								<v-btn
									@click="deleteExpense(expense)"
									color="red"
									variant="outlined"
									size="small"
									rounded="lg"
								>
									<v-icon size="16" class="mr-1"
										>mdi-delete</v-icon
									>
									Xóa
								</v-btn>
							</template>
							<template v-else>
								<v-spacer></v-spacer>
								<v-icon
									color="grey-lighten-1"
									size="20"
									v-tooltip="'Không có quyền sửa'"
									>mdi-lock</v-icon
								>
							</template>
						</v-card-actions>
					</v-card>
				</v-col>
			</v-row>
		</div>

		<div v-else class="empty-state">
			<v-card class="empty-card text-center pa-12" rounded="xl">
				<div class="empty-icon mb-6">
					<v-icon size="96" color="surface-variant"
						>mdi-receipt-text-outline</v-icon
					>
					<div class="empty-decoration"></div>
				</div>
				<h3 class="empty-title text-2xl font-bold mb-4">
					Không tìm thấy khoản chi tiêu nào
				</h3>
				<p class="empty-subtitle text-lg text-on-surface-variant mb-8">
					Thử thay đổi bộ lọc hoặc tạo khoản chi mới
				</p>
				<v-btn
					color="primary"
					@click="openAddDialog"
					size="large"
					rounded="xl"
				>
					<v-icon size="20" class="mr-2">mdi-plus</v-icon>
					Tạo khoản chi tiêu
				</v-btn>
			</v-card>
		</div>

		<v-dialog v-model="dialog" max-width="1000px" persistent scrollable>
			<v-card class="dialog-card" rounded="xl">
				<div class="dialog-header pa-6 pb-0">
					<div class="d-flex align-center">
						<div class="dialog-icon mr-4">
							<v-icon size="24" color="white">
								{{
									editedIndex === -1
										? "mdi-plus"
										: "mdi-pencil"
								}}
							</v-icon>
						</div>
						<div>
							<h3 class="dialog-title text-xl font-bold">
								{{
									editedIndex === -1
										? "Thêm khoản chi tiêu mới"
										: "Sửa khoản chi tiêu"
								}}
							</h3>
							<p class="dialog-subtitle text-sm">
								{{
									editedIndex === -1
										? "Tạo khoản chi tiêu mới cho nhóm"
										: "Cập nhật thông tin chi tiêu"
								}}
							</p>
						</div>
					</div>
				</div>

				<v-card-text class="pa-6" style="max-height: 70vh">
					<v-form ref="form" v-model="valid">
						<div class="form-section mb-6">
							<h4 class="section-title mb-4">Thông tin cơ bản</h4>
							<v-row>
								<v-col cols="12" md="6">
									<div class="form-group">
										<label class="form-label"
											>Tên khoản chi tiêu *</label
										>
										<v-text-field
											v-model="editedItem.name"
											variant="outlined"
											:rules="[
												(v) => !!v || 'Tên là bắt buộc',
											]"
											required
											hide-details="auto"
											rounded="lg"
										>
											<template v-slot:prepend-inner>
												<v-icon color="primary"
													>mdi-receipt</v-icon
												>
											</template>
										</v-text-field>
									</div>
								</v-col>

								<v-col cols="12" md="6">
									<div class="form-group">
										<label class="form-label"
											>Tổng số tiền (VND) *</label
										>
										<v-text-field
											v-model.number="
												editedItem.total_amount
											"
											type="number"
											variant="outlined"
											:rules="[
												(v) =>
													!!v ||
													'Số tiền là bắt buộc',
												(v) =>
													v > 0 ||
													'Số tiền phải lớn hơn 0',
											]"
											required
											hide-details="auto"
											rounded="lg"
										>
											<template v-slot:prepend-inner>
												<v-icon color="primary"
													>mdi-currency-usd</v-icon
												>
											</template>
										</v-text-field>
									</div>
								</v-col>

								<v-col cols="12">
									<div class="form-group">
										<label class="form-label"
											>Người trả tiền *</label
										>
										<v-select
											v-model="editedItem.payer_id"
											:items="members"
											item-title="name"
											item-value="id"
											variant="outlined"
											:rules="[
												(v) =>
													!!v ||
													'Người trả là bắt buộc',
											]"
											required
											hide-details="auto"
											rounded="lg"
										>
											<template v-slot:prepend-inner>
												<v-icon color="primary"
													>mdi-account-cash</v-icon
												>
											</template>
										</v-select>
									</div>
								</v-col>
							</v-row>
						</div>

						<div class="form-section">
							<div class="participants-header mb-4">
								<h4 class="section-title">Người tham gia</h4>
								<div class="participants-actions">
									<v-btn
										@click="distributeEvenly"
										size="small"
										color="success"
										variant="outlined"
										rounded="lg"
										class="mr-2"
									>
										<v-icon size="16" class="mr-1"
											>mdi-calculator</v-icon
										>
										Chia đều
									</v-btn>
									<v-btn
										@click="addParticipant"
										color="primary"
										size="small"
										rounded="lg"
									>
										<v-icon size="16" class="mr-1"
											>mdi-plus</v-icon
										>
										Thêm người
									</v-btn>
								</div>
							</div>

							<v-expand-transition>
								<v-alert
									v-if="totalError"
									type="error"
									class="mb-4"
									rounded="lg"
									border="start"
									variant="tonal"
								>
									<template v-slot:prepend>
										<v-icon>mdi-alert-circle</v-icon>
									</template>
									<div class="alert-content">
										<div class="font-weight-medium">
											Tổng tiền không khớp
										</div>
										<div class="text-sm mt-1">
											Tổng tiền người tham gia ({{
												formatCurrency(
													participantTotal
												)
											}}) phải bằng tổng số tiền ({{
												formatCurrency(
													editedItem.total_amount
												)
											}})
										</div>
									</div>
								</v-alert>
							</v-expand-transition>

							<div
								v-if="editedItem.participant_data.length === 0"
								class="empty-participants text-center py-8"
							>
								<v-icon size="48" color="surface-variant"
									>mdi-account-plus</v-icon
								>
								<p class="text-surface-variant mt-2">
									Chưa có người tham gia nào
								</p>
							</div>

							<div v-else class="participants-list">
								<div
									v-for="(
										participant, index
									) in editedItem.participant_data"
									:key="index"
									class="participant-item mb-3"
								>
									<v-card
										variant="outlined"
										class="pa-4"
										rounded="lg"
									>
										<v-row align="center">
											<v-col cols="12" md="4">
												<div class="form-group">
													<label
														class="form-label-small"
														>Thành viên</label
													>
													<v-select
														v-model="
															participant.member_id
														"
														:items="members"
														item-title="name"
														item-value="id"
														variant="outlined"
														density="compact"
														hide-details
														rounded="lg"
													></v-select>
												</div>
											</v-col>
											<v-col cols="12" md="3">
												<div class="form-group">
													<label
														class="form-label-small"
														>Số tiền (VND)</label
													>
													<v-text-field
														v-model.number="
															participant.amount_owed
														"
														type="number"
														variant="outlined"
														density="compact"
														hide-details
														rounded="lg"
													></v-text-field>
												</div>
											</v-col>
											<v-col cols="12" md="3">
												<div class="form-group">
													<label
														class="form-label-small"
														>Trạng thái</label
													>
													<div class="pt-2">
														<v-switch
															v-model="
																participant.is_paid
															"
															color="success"
															:label="
																participant.is_paid
																	? 'Đã trả'
																	: 'Chưa trả'
															"
															hide-details
															density="compact"
														></v-switch>
													</div>
												</div>
											</v-col>
											<v-col cols="12" md="2">
												<div
													class="d-flex justify-center"
												>
													<v-btn
														@click="
															removeParticipant(
																index
															)
														"
														icon
														size="small"
														color="error"
														variant="outlined"
														rounded="lg"
													>
														<v-icon size="18"
															>mdi-delete</v-icon
														>
													</v-btn>
												</div>
											</v-col>
										</v-row>
									</v-card>
								</div>
							</div>
						</div>
					</v-form>
				</v-card-text>

				<v-card-actions class="pa-6 pt-0">
					<v-spacer></v-spacer>
					<v-btn
						color="surface-variant"
						variant="outlined"
						@click="close"
						rounded="lg"
						class="mr-3"
					>
						<v-icon size="18" class="mr-2">mdi-close</v-icon>
						Hủy
					</v-btn>
					<v-btn
						color="primary"
						@click="save"
						:disabled="
							!valid ||
							totalError ||
							editedItem.participant_data.length === 0
						"
						:loading="saving"
						rounded="lg"
					>
						<v-icon size="18" class="mr-2">mdi-check</v-icon>
						Lưu
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

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
import { expensesApi, membersApi } from "../services/api";

const dialog = ref(false);
const valid = ref(false);
const saving = ref(false);
const editedIndex = ref(-1);
const expenses = ref([]);
const members = ref([]);

// Filters
const search = ref("");
const selectedPayer = ref(null);

// Snackbar for notifications
const snackbar = reactive({
	show: false,
	text: "",
	color: "success",
	icon: "mdi-check-circle",
});

const editedItem = ref({
	name: "",
	total_amount: 0,
	payer_id: null,
	participant_data: [],
});

const defaultItem = {
	name: "",
	total_amount: 0,
	payer_id: null,
	participant_data: [],
};

const participantTotal = computed(() => {
	return editedItem.value.participant_data.reduce(
		(sum: number, p: any) => sum + (p.amount_owed || 0),
		0
	);
});

const totalError = computed(() => {
	return (
		Math.abs(participantTotal.value - editedItem.value.total_amount) >
			0.01 && editedItem.value.total_amount > 0
	);
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

// Search and Filter Handlers
let filterTimeout: any = null;
const handleSearch = (val: string) => {
	if (filterTimeout) clearTimeout(filterTimeout);
	filterTimeout = setTimeout(() => fetchExpenses(), 500);
};

const handleFilter = (val: any) => {
	fetchExpenses();
};

const fetchExpenses = async () => {
	try {
		const response = await expensesApi.getAll(
			search.value,
			selectedPayer.value
		);
		expenses.value = response.data;
	} catch (error) {
		console.error("Error fetching expenses:", error);
		showNotification(
			"Có lỗi khi tải danh sách chi tiêu",
			"error",
			"mdi-alert-circle"
		);
	}
};

const fetchMembers = async () => {
	try {
		const response = await membersApi.getAll();
		members.value = response.data;
	} catch (error) {
		console.error("Error fetching members:", error);
		showNotification(
			"Có lỗi khi tải danh sách thành viên",
			"error",
			"mdi-alert-circle"
		);
	}
};

const getStatusColor = (expense: any) => {
	const paidCount = expense.participants.filter((p: any) => p.is_paid).length;
	const totalCount = expense.participants.length;

	if (paidCount === totalCount) return "success";
	if (paidCount === 0) return "error";
	return "warning";
};

const getStatusText = (expense: any) => {
	const paidCount = expense.participants.filter((p: any) => p.is_paid).length;
	const totalCount = expense.participants.length;

	if (paidCount === totalCount) return "Hoàn thành";
	if (paidCount === 0) return "Chưa thanh toán";
	return `${paidCount}/${totalCount} đã trả`;
};

const openAddDialog = () => {
	editedIndex.value = -1;
	editedItem.value = { ...defaultItem, participant_data: [] };
	dialog.value = true;
};

const editExpense = (expense: any) => {
	editedIndex.value = expenses.value.indexOf(expense);
	editedItem.value = {
		...expense,
		payer_id: expense.payer.id,
		participant_data: expense.participants.map((p: any) => ({
			member_id: p.member.id,
			amount_owed: p.amount_owed,
			is_paid: p.is_paid,
		})),
	};
	dialog.value = true;
};

const deleteExpense = async (expense: any) => {
	if (confirm(`Bạn có chắc muốn xóa khoản chi tiêu "${expense.name}"?`)) {
		try {
			await expensesApi.delete(expense.id);
			await fetchExpenses();
			showNotification(
				`Đã xóa khoản chi tiêu "${expense.name}" thành công`
			);
		} catch (error: any) {
			console.error("Error deleting expense:", error);
			const msg =
				error.response?.data?.error || "Có lỗi khi xóa khoản chi tiêu";
			showNotification(msg, "error", "mdi-alert-circle");
		}
	}
};

const addParticipant = () => {
	editedItem.value.participant_data.push({
		member_id: null,
		amount_owed: 0,
		is_paid: false,
	});
};

const removeParticipant = (index: number) => {
	editedItem.value.participant_data.splice(index, 1);
};

const distributeEvenly = () => {
	const count = editedItem.value.participant_data.length;
	if (count > 0 && editedItem.value.total_amount > 0) {
		const amount =
			Math.round((editedItem.value.total_amount / count) * 100) / 100;
		editedItem.value.participant_data.forEach((p: any) => {
			p.amount_owed = amount;
		});
	}
};

const close = () => {
	dialog.value = false;
	editedItem.value = { ...defaultItem };
	editedIndex.value = -1;
};

const save = async () => {
	saving.value = true;
	try {
		if (editedIndex.value > -1) {
			await expensesApi.update(editedItem.value.id, editedItem.value);
			showNotification("Cập nhật khoản chi tiêu thành công");
		} else {
			await expensesApi.create(editedItem.value);
			showNotification("Thêm khoản chi tiêu mới thành công");
		}
		await fetchExpenses();
		close();
	} catch (error: any) {
		console.error("Error saving expense:", error);
		const msg =
			error.response?.data?.error || "Có lỗi khi lưu khoản chi tiêu";
		showNotification(msg, "error", "mdi-alert-circle");
	} finally {
		saving.value = false;
	}
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

onMounted(() => {
	fetchExpenses();
	fetchMembers();
});
</script>

<style scoped>
.expenses-page {
	max-width: 1200px;
	margin: 0 auto;
}

.page-header {
	position: relative;
}

.header-content {
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex-wrap: wrap;
	gap: 1rem;
}

.header-icon-title {
	display: flex;
	align-items: center;
	gap: 1rem;
}

.page-icon {
	width: 64px;
	height: 64px;
	border-radius: 16px;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
}

.page-title {
	background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	line-height: 1.2;
	margin-bottom: 0.5rem;
}

.page-subtitle {
	color: rgb(107, 114, 128);
	font-size: 1rem;
	margin: 0;
}

.add-btn {
	font-weight: 500;
	text-transform: none;
	box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
}

.add-btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

.expense-card {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	transition: all 0.3s ease;
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

.dialog-card {
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(20px);
	border: 1px solid rgba(102, 126, 234, 0.1);
}

.dialog-header {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 16px 16px 0 0;
}

.dialog-icon {
	width: 48px;
	height: 48px;
	border-radius: 12px;
	background: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
}

.dialog-title {
	color: white;
	margin-bottom: 0.25rem;
}

.dialog-subtitle {
	color: rgba(255, 255, 255, 0.8);
	margin: 0;
}

.form-section {
	padding: 1.5rem;
	border-radius: 12px;
	background: rgba(248, 250, 252, 0.5);
	border: 1px solid rgba(102, 126, 234, 0.1);
}

.section-title {
	font-weight: 600;
	color: rgb(55, 65, 81);
	margin: 0;
}

.participants-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex-wrap: wrap;
	gap: 1rem;
}

.participants-actions {
	display: flex;
	gap: 0.5rem;
}

.form-group {
	margin-bottom: 0.5rem;
}

.form-label {
	display: block;
	font-weight: 500;
	color: rgb(55, 65, 81);
	margin-bottom: 0.5rem;
	font-size: 0.875rem;
}

.form-label-small {
	display: block;
	font-weight: 500;
	color: rgb(55, 65, 81);
	margin-bottom: 0.25rem;
	font-size: 0.75rem;
}

.alert-content {
	display: flex;
	flex-direction: column;
}

.empty-participants {
	padding: 2rem;
	border: 2px dashed rgba(102, 126, 234, 0.2);
	border-radius: 12px;
	background: rgba(248, 250, 252, 0.5);
}

.participants-list {
	max-height: 300px;
	overflow-y: auto;
}

.participant-item {
	position: relative;
}

.modern-snackbar {
	backdrop-filter: blur(10px);
}

/* Styles for Filter Bar */
.glass-effect {
	background: rgba(255, 255, 255, 0.8) !important;
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
}

/* --- FIX FOR SQUARE BORDER ON CHECKBOXES/SWITCHES --- */
/* Nguyên nhân: Xung đột giữa Tailwind CSS Preflight và Vuetify */
:deep(input[type="checkbox"]),
:deep(input[type="radio"]) {
	position: absolute !important;
	opacity: 0 !important;
	width: 0 !important;
	height: 0 !important;
	margin: 0 !important;
	padding: 0 !important;
	pointer-events: none !important;
}

/* Ẩn mũi tên input number */
:deep(input[type="number"]::-webkit-outer-spin-button),
:deep(input[type="number"]::-webkit-inner-spin-button) {
	-webkit-appearance: none;
	margin: 0;
}

@media (max-width: 768px) {
	.header-content {
		flex-direction: column;
		align-items: stretch;
	}

	.header-icon-title {
		justify-content: center;
		text-align: center;
	}

	.page-icon {
		width: 48px;
		height: 48px;
	}

	.participants-header {
		flex-direction: column;
		align-items: stretch;
	}

	.participants-actions {
		justify-content: stretch;
		gap: 0.5rem;
	}

	.participants-actions .v-btn {
		flex: 1;
	}
}

@media (max-width: 600px) {
	.expense-card {
		margin-bottom: 1rem;
	}

	.card-header {
		padding: 1rem !important;
	}

	.expense-title {
		font-size: 1rem;
	}

	.expense-amount {
		font-size: 1.25rem;
	}

	.dialog-card {
		margin: 1rem;
		max-width: calc(100vw - 2rem) !important;
	}
}

/* Form validation */
:deep(.v-field--error) {
	animation: shake 0.3s ease-in-out;
}

@keyframes shake {
	0%,
	100% {
		transform: translateX(0);
	}
	25% {
		transform: translateX(-2px);
	}
	75% {
		transform: translateX(2px);
	}
}

/* Scrollbar for participants list */
.participants-list::-webkit-scrollbar {
	width: 6px;
}

.participants-list::-webkit-scrollbar-thumb {
	background: rgba(102, 126, 234, 0.3);
	border-radius: 3px;
}
</style>
