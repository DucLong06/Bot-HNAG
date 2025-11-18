<template>
	<div class="members-page">
		<div class="page-header mb-8">
			<div class="header-content">
				<div class="header-text">
					<div class="header-icon-title">
						<div class="page-icon">
							<v-icon size="32" color="white"
								>mdi-account-group</v-icon
							>
						</div>
						<div>
							<h1 class="page-title text-3xl font-bold">
								Quản lý thành viên
							</h1>
							<p class="page-subtitle">
								Quản lý danh sách thành viên tham gia chi tiêu
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
						Thêm thành viên
					</v-btn>
				</div>
			</div>
		</div>

		<v-card class="members-card" rounded="xl" elevation="0">
			<div class="card-header pa-6 pb-0">
				<div class="d-flex align-center justify-space-between">
					<div class="card-title-section">
						<h2
							class="card-title text-xl font-bold d-flex align-center"
						>
							<v-icon class="mr-3" color="primary"
								>mdi-account-multiple</v-icon
							>
							Danh sách thành viên
						</h2>
						<p class="card-subtitle text-sm">
							{{ members.length }} thành viên đã đăng ký
						</p>
					</div>

					<div class="search-section">
						<v-text-field
							v-model="search"
							density="compact"
							label="Tìm kiếm thành viên"
							variant="outlined"
							rounded="lg"
							class="search-input"
							style="min-width: 250px"
							hide-details
							single-line
							@update:model-value="handleSearch"
						>
							<template v-slot:prepend-inner>
								<v-icon color="surface-variant"
									>mdi-magnify</v-icon
								>
							</template>
						</v-text-field>
					</div>
				</div>
			</div>

			<div class="table-container pa-6 pt-4">
				<v-data-table
					:headers="headers"
					:items="members"
					class="modern-table"
					:loading="loading"
					loading-text="Đang tải dữ liệu..."
					no-data-text="Không có thành viên nào"
					items-per-page="10"
					rounded="lg"
				>
					<template v-slot:item.name="{ item }">
						<div class="member-info d-flex align-center">
							<v-avatar color="primary" class="mr-3" size="32">
								<span class="text-white font-weight-bold">
									{{ item.name.charAt(0).toUpperCase() }}
								</span>
							</v-avatar>
							<div>
								<div class="member-name font-weight-medium">
									{{ item.name }}
								</div>
							</div>
						</div>
					</template>

					<template v-slot:item.telegram_id="{ item }">
						<v-chip
							color="info"
							size="small"
							rounded="lg"
							variant="tonal"
						>
							<v-icon size="12" class="mr-1">mdi-telegram</v-icon>
							{{ item.telegram_id }}
						</v-chip>
					</template>

					<template v-slot:item.bank_name="{ item }">
						<div v-if="item.bank_name" class="bank-info">
							<v-chip
								color="success"
								size="small"
								variant="tonal"
								rounded="lg"
							>
								<v-icon size="12" class="mr-1">mdi-bank</v-icon>
								{{ item.bank_name }}
							</v-chip>
						</div>
						<span v-else class="text-surface-variant">—</span>
					</template>

					<template v-slot:item.account_number="{ item }">
						<div v-if="item.account_number" class="account-number">
							<v-chip
								color="orange"
								size="small"
								variant="tonal"
								rounded="lg"
							>
								<v-icon size="12" class="mr-1"
									>mdi-credit-card</v-icon
								>
								{{ item.account_number }}
							</v-chip>
						</div>
						<span v-else class="text-surface-variant">—</span>
					</template>

					<template v-slot:item.created_at="{ item }">
						<div class="date-info">
							<div class="date-text">
								{{ formatDate(item.created_at) }}
							</div>
							<div class="time-text text-xs text-surface-variant">
								{{ formatTime(item.created_at) }}
							</div>
						</div>
					</template>

					<template v-slot:item.actions="{ item }">
						<div class="action-buttons">
							<v-btn
								icon
								size="small"
								color="error"
								variant="text"
								@click="viewDebtSummary(item)"
								class="action-btn"
								v-tooltip="'Xem công nợ'"
							>
								<v-icon size="18">mdi-cash-multiple</v-icon>
							</v-btn>
							<v-btn
								icon
								size="small"
								color="orange"
								variant="text"
								@click="editMember(item)"
								class="action-btn"
							>
								<v-icon size="18">mdi-pencil</v-icon>
							</v-btn>
							<v-btn
								icon
								size="small"
								color="red"
								variant="text"
								@click="deleteMember(item)"
								class="action-btn"
							>
								<v-icon size="18">mdi-delete</v-icon>
							</v-btn>
						</div>
					</template>
				</v-data-table>
			</div>
		</v-card>

		<v-dialog v-model="dialog" max-width="600px" persistent>
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
										? "Thêm thành viên mới"
										: "Sửa thành viên"
								}}
							</h3>
							<p class="dialog-subtitle text-sm">
								{{
									editedIndex === -1
										? "Nhập thông tin thành viên mới"
										: "Cập nhật thông tin thành viên"
								}}
							</p>
						</div>
					</div>
				</div>

				<v-card-text class="pa-6">
					<v-form ref="form" v-model="valid">
						<div class="form-sections">
							<div class="form-section mb-6">
								<h4 class="section-title mb-4">
									Thông tin cơ bản
								</h4>

								<div class="form-group mb-4">
									<label class="form-label"
										>Tên thành viên *</label
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
												>mdi-account</v-icon
											>
										</template>
									</v-text-field>
								</div>

								<div class="form-group">
									<label class="form-label"
										>Telegram ID *</label
									>
									<v-text-field
										v-model="editedItem.telegram_id"
										variant="outlined"
										:rules="[
											(v) =>
												!!v ||
												'Telegram ID là bắt buộc',
										]"
										required
										hide-details="auto"
										rounded="lg"
									>
										<template v-slot:prepend-inner>
											<v-icon color="primary"
												>mdi-telegram</v-icon
											>
										</template>
									</v-text-field>
									<div class="form-hint">
										ID Telegram để gửi nhắc nhở thanh toán
									</div>
								</div>
							</div>

							<div class="form-section">
								<h4 class="section-title mb-4">
									Thông tin ngân hàng (Tùy chọn)
								</h4>

								<div class="form-group mb-4">
									<label class="form-label">Ngân hàng</label>
									<v-select
										v-model="editedItem.bank_name"
										:items="bankOptions"
										variant="outlined"
										hide-details="auto"
										rounded="lg"
									>
										<template v-slot:prepend-inner>
											<v-icon color="primary"
												>mdi-bank</v-icon
											>
										</template>
									</v-select>
								</div>

								<div class="form-group">
									<label class="form-label"
										>Số tài khoản</label
									>
									<v-text-field
										v-model="editedItem.account_number"
										variant="outlined"
										hide-details="auto"
										rounded="lg"
									>
										<template v-slot:prepend-inner>
											<v-icon color="primary"
												>mdi-credit-card</v-icon
											>
										</template>
									</v-text-field>
									<div class="form-hint">
										Số tài khoản ngân hàng để nhận tiền
									</div>
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
						:disabled="!valid"
						:loading="saving"
						rounded="lg"
					>
						<v-icon size="18" class="mr-2">mdi-check</v-icon>
						Lưu
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="debtDialog" max-width="800px" scrollable>
			<v-card class="dialog-card" rounded="xl" v-if="debtSummary">
				<div class="dialog-header pa-6 error-gradient">
					<div class="d-flex align-center justify-space-between">
						<div class="d-flex align-center">
							<v-avatar
								color="white"
								size="48"
								class="mr-4 elevation-2"
							>
								<span
									class="text-error font-weight-bold text-xl"
								>
									{{
										debtSummary.member_name
											.charAt(0)
											.toUpperCase()
									}}
								</span>
							</v-avatar>
							<div>
								<h3 class="text-xl font-bold text-white">
									Công nợ: {{ debtSummary.member_name }}
								</h3>
								<p class="text-white/90 text-sm">
									Tổng số khoản nợ:
									{{ debtSummary.debt_count }}
								</p>
							</div>
						</div>
						<div class="text-right">
							<div class="text-white/80 text-sm">
								Tổng phải trả
							</div>
							<div class="text-2xl font-bold text-white">
								{{ formatCurrency(debtSummary.total_owed) }}
							</div>
						</div>
					</div>
				</div>

				<v-card-text class="pa-6" style="max-height: 70vh">
					<div v-if="debtSummary.details.length > 0">
						<div
							v-for="detail in debtSummary.details"
							:key="detail.payer_id"
							class="mb-6"
						>
							<v-card
								variant="outlined"
								class="pa-4 payer-card"
								rounded="lg"
							>
								<div
									class="d-flex flex-column flex-sm-row align-start align-sm-center justify-space-between mb-4"
								>
									<div
										class="d-flex align-center mb-2 mb-sm-0"
									>
										<v-icon
											color="primary"
											class="mr-2"
											size="24"
											>mdi-account-cash</v-icon
										>
										<div>
											<div
												class="font-weight-bold text-lg"
											>
												Trả cho: {{ detail.payer_name }}
											</div>
											<div
												class="text-caption text-surface-variant"
												v-if="detail.bank_name"
											>
												{{ detail.bank_name }} -
												{{ detail.account_number }}
											</div>
										</div>
									</div>
									<div class="d-flex align-center">
										<v-btn
											v-if="
												detail.bank_name &&
												detail.account_number
											"
											size="small"
											variant="tonal"
											color="primary"
											class="mr-3"
											rounded="lg"
											@click="
												showQuickQr(
													detail,
													debtSummary.member_name
												)
											"
										>
											<v-icon start>mdi-qrcode</v-icon>
											Mã QR
										</v-btn>

										<v-chip
											color="error"
											variant="elevated"
											rounded="lg"
										>
											Nợ:
											{{
												formatCurrency(
													detail.total_owed_to_payer
												)
											}}
										</v-chip>
									</div>
								</div>

								<v-divider class="mb-3"></v-divider>

								<div class="expense-list">
									<div
										v-for="expense in detail.expenses"
										:key="expense.expense_id"
										class="expense-item d-flex justify-space-between align-center py-2"
									>
										<div>
											<div class="font-weight-medium">
												{{ expense.expense_name }}
											</div>
											<div
												class="text-caption text-surface-variant"
											>
												{{ formatDate(expense.date) }}
											</div>
										</div>
										<div
											class="font-weight-bold text-error"
										>
											{{ formatCurrency(expense.amount) }}
										</div>
									</div>
								</div>
							</v-card>
						</div>
					</div>
					<div v-else class="text-center py-12">
						<v-icon size="64" color="success" class="mb-4"
							>mdi-check-circle-outline</v-icon
						>
						<h3 class="text-xl font-bold text-success">
							Không có khoản nợ nào!
						</h3>
						<p class="text-surface-variant">
							Thành viên này đã thanh toán đầy đủ.
						</p>
					</div>
				</v-card-text>

				<v-card-actions class="pa-6 pt-0">
					<v-spacer></v-spacer>
					<v-btn
						color="primary"
						variant="elevated"
						@click="debtDialog = false"
						rounded="lg"
						block
					>
						Đóng
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="qrDialog" max-width="400px">
			<v-card rounded="xl">
				<v-card-title class="text-center pt-6 font-bold">
					Quét mã thanh toán
				</v-card-title>
				<v-card-text class="text-center pa-6">
					<div v-if="qrLoading" class="d-flex justify-center py-8">
						<v-progress-circular
							indeterminate
							color="primary"
						></v-progress-circular>
					</div>
					<img
						v-show="!qrLoading"
						:src="qrUrl"
						class="w-100 rounded-lg border"
						@load="qrLoading = false"
						alt="VietQR"
					/>
					<div class="mt-4 text-body-2 text-surface-variant">
						Số tiền: <strong>{{ qrAmount }}</strong>
						<br />
						Nội dung: {{ qrDesc }}
					</div>
				</v-card-text>
				<v-card-actions class="pb-6 justify-center">
					<v-btn
						color="primary"
						variant="tonal"
						rounded="lg"
						@click="qrDialog = false"
					>
						Đóng
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="deleteDialog" max-width="450px">
			<v-card class="delete-dialog" rounded="xl">
				<div class="delete-header pa-6 pb-0">
					<div class="d-flex align-center">
						<div class="delete-icon mr-4">
							<v-icon size="24" color="white">mdi-delete</v-icon>
						</div>
						<div>
							<h3
								class="delete-title text-xl font-bold text-white"
							>
								Xác nhận xóa
							</h3>
						</div>
					</div>
				</div>

				<v-card-text class="pa-6">
					<p class="delete-message mb-4">
						Bạn có chắc muốn xóa thành viên
						<strong>{{ memberToDelete?.name }}</strong
						>?
					</p>

					<v-alert type="warning" variant="tonal" rounded="lg">
						<template v-slot:prepend>
							<v-icon>mdi-alert-triangle</v-icon>
						</template>
						Hành động này không thể hoàn tác và sẽ xóa tất cả dữ
						liệu liên quan!
					</v-alert>
				</v-card-text>

				<v-card-actions class="pa-6 pt-0">
					<v-spacer></v-spacer>
					<v-btn
						color="surface-variant"
						variant="outlined"
						@click="deleteDialog = false"
						rounded="lg"
						class="mr-3"
					>
						Hủy
					</v-btn>
					<v-btn
						color="error"
						@click="confirmDelete"
						:loading="deleting"
						rounded="lg"
					>
						<v-icon size="18" class="mr-2">mdi-delete</v-icon>
						Xóa
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
import { ref, reactive, onMounted } from "vue";
import { membersApi, telegramApi } from "../services/api";

const search = ref("");
const dialog = ref(false);
const deleteDialog = ref(false);
const debtDialog = ref(false);
const valid = ref(false);
const loading = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editedIndex = ref(-1);
const members = ref([]);
const memberToDelete = ref(null);
const debtSummary = ref(null as any);

// QR Logic
const qrDialog = ref(false);
const qrLoading = ref(false);
const qrUrl = ref("");
const qrAmount = ref("");
const qrDesc = ref("");

const showQuickQr = async (detail: any, debtorName: string) => {
	if (!detail.bank_name || !detail.account_number) {
		showNotification(
			"Không có thông tin ngân hàng để tạo QR.",
			"warning",
			"mdi-alert-circle"
		);
		return;
	}

	qrLoading.value = true;
	qrDialog.value = true;

	const accountName = detail.payer_name;
	const rawDescription = `${debtorName} tra ${accountName}`;

	try {
		// GỌI API BACKEND ĐỂ TẠO URL QR
		const response = await telegramApi.generateQrCode({
			bank_name: detail.bank_name,
			account_number: detail.account_number,
			amount: detail.total_owed_to_payer,
			description: rawDescription,
			account_name: accountName,
		});

		qrUrl.value = response.data.qr_url;
		qrAmount.value = formatCurrency(detail.total_owed_to_payer);

		// Cần phải decode URL để lấy nội dung đã được làm sạch từ BE
		const urlParams = new URLSearchParams(
			response.data.qr_url.split("?")[1]
		);
		const addInfo = urlParams.get("addInfo") || rawDescription;
		qrDesc.value = decodeURIComponent(addInfo);
	} catch (error) {
		console.error("Error generating QR code:", error);
		showNotification(
			"Lỗi tạo mã QR. Vui lòng kiểm tra thông tin ngân hàng.",
			"error",
			"mdi-alert-circle"
		);
		qrDialog.value = false;
	} finally {
		qrLoading.value = false;
	}
};

// Snackbar for notifications
const snackbar = reactive({
	show: false,
	text: "",
	color: "success",
	icon: "mdi-check-circle",
});

const bankOptions = [
	"Vietcombank",
	"Techcombank",
	"BIDV",
	"VietinBank",
	"Agribank",
	"MB Bank",
	"ACB",
	"Sacombank",
	"Eximbank",
	"SHB",
	"TPBank",
	"VPBank",
	"HDBank",
	"OCB",
	"LienVietPostBank",
	"SeABank",
	"VIB",
	"MSB",
	"Nam A Bank",
	"Bac A Bank",
];

const headers = [
	{ title: "Thành viên", key: "name", width: "25%" },
	{ title: "Telegram ID", key: "telegram_id", width: "20%" },
	{ title: "Ngân hàng", key: "bank_name", width: "15%" },
	{ title: "Số TK", key: "account_number", width: "15%" },
	{ title: "Ngày tạo", key: "created_at", width: "15%" },
	{ title: "Hành động", key: "actions", sortable: false, width: "10%" },
];

const editedItem = ref({
	name: "",
	telegram_id: "",
	bank_name: "",
	account_number: "",
});

const defaultItem = {
	name: "",
	telegram_id: "",
	bank_name: "",
	account_number: "",
};

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

const fetchMembers = async () => {
	loading.value = true;
	try {
		const response = await membersApi.getAll(search.value);
		members.value = response.data;
	} catch (error) {
		console.error("Error fetching members:", error);
		showNotification(
			"Có lỗi khi tải danh sách thành viên",
			"error",
			"mdi-alert-circle"
		);
	} finally {
		loading.value = false;
	}
};

// Debounce search input
let searchTimeout: any = null;
const handleSearch = (val: string) => {
	if (searchTimeout) clearTimeout(searchTimeout);
	searchTimeout = setTimeout(() => {
		fetchMembers();
	}, 500);
};

const openAddDialog = () => {
	editedIndex.value = -1;
	editedItem.value = { ...defaultItem };
	dialog.value = true;
};

const editMember = (member: any) => {
	editedIndex.value = members.value.indexOf(member);
	editedItem.value = { ...member };
	dialog.value = true;
};

// New function: View Debt Summary
const viewDebtSummary = async (member: any) => {
	try {
		const response = await membersApi.getDebtSummary(member.id);
		debtSummary.value = response.data;
		debtDialog.value = true;
	} catch (error) {
		console.error("Error fetching debt summary:", error);
		showNotification(
			"Có lỗi khi tải thông tin công nợ",
			"error",
			"mdi-alert-circle"
		);
	}
};

const deleteMember = (member: any) => {
	memberToDelete.value = member;
	deleteDialog.value = true;
};

const confirmDelete = async () => {
	if (!memberToDelete.value) return;

	deleting.value = true;
	try {
		await membersApi.delete(memberToDelete.value.id);
		await fetchMembers();
		deleteDialog.value = false;
		memberToDelete.value = null;
		showNotification(
			`Đã xóa thành viên ${memberToDelete.value?.name || ""} thành công`
		);
	} catch (error) {
		console.error("Error deleting member:", error);
		showNotification(
			"Có lỗi khi xóa thành viên",
			"error",
			"mdi-alert-circle"
		);
	} finally {
		deleting.value = false;
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
			await membersApi.update(editedItem.value.id, editedItem.value);
			showNotification("Cập nhật thành viên thành công");
		} else {
			await membersApi.create(editedItem.value);
			showNotification("Thêm thành viên mới thành công");
		}
		await fetchMembers();
		close();
	} catch (error) {
		console.error("Error saving member:", error);
		showNotification(
			"Có lỗi khi lưu thông tin thành viên",
			"error",
			"mdi-alert-circle"
		);
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

const formatTime = (dateString: string) => {
	return new Date(dateString).toLocaleTimeString("vi-VN", {
		hour: "2-digit",
		minute: "2-digit",
	});
};

onMounted(fetchMembers);
</script>

<style scoped>
.members-page {
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

.members-card {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
}

.card-header {
	border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.card-title {
	color: rgb(31, 41, 55);
	margin-bottom: 0.25rem;
}

.card-subtitle {
	color: rgb(107, 114, 128);
	margin: 0;
}

.search-input :deep(.v-field) {
	background: rgba(248, 250, 252, 0.8);
	border: 1px solid rgba(102, 126, 234, 0.2);
}

.search-input :deep(.v-field--focused) {
	border-color: rgba(102, 126, 234, 0.5);
	box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modern-table :deep(.v-data-table__th) {
	background: rgba(102, 126, 234, 0.05);
	font-weight: 600;
	color: rgb(55, 65, 81);
	border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.modern-table :deep(.v-data-table__tr:hover) {
	background: rgba(102, 126, 234, 0.03);
}

.modern-table :deep(.v-data-table__td) {
	border-bottom: 1px solid rgba(102, 126, 234, 0.05);
}

.member-info {
	padding: 0.5rem 0;
}

.member-name {
	color: rgb(31, 41, 55);
	font-size: 0.875rem;
}

.date-info {
	text-align: left;
}

.date-text {
	font-size: 0.875rem;
	font-weight: 500;
	color: rgb(55, 65, 81);
}

.time-text {
	margin-top: 0.125rem;
}

.action-buttons {
	display: flex;
	gap: 0.25rem;
}

.action-btn {
	transition: transform 0.2s ease;
}

.action-btn:hover {
	transform: scale(1.1);
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

.form-sections {
	width: 100%;
}

.form-section {
	padding: 1rem;
	border-radius: 12px;
	background: rgba(248, 250, 252, 0.5);
	border: 1px solid rgba(102, 126, 234, 0.1);
}

.section-title {
	font-weight: 600;
	color: rgb(55, 65, 81);
	margin-bottom: 1rem;
}

.form-group {
	margin-bottom: 1rem;
}

.form-label {
	display: block;
	font-weight: 500;
	color: rgb(55, 65, 81);
	margin-bottom: 0.5rem;
	font-size: 0.875rem;
}

.form-hint {
	margin-top: 0.25rem;
	font-size: 0.75rem;
	color: rgb(107, 114, 128);
}

.delete-dialog {
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(20px);
}

.delete-header {
	background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
	border-radius: 16px 16px 0 0;
}

.delete-icon {
	width: 48px;
	height: 48px;
	border-radius: 12px;
	background: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
}

.delete-title {
	margin: 0;
}

.delete-message {
	color: rgb(55, 65, 81);
	font-size: 1rem;
	line-height: 1.5;
}

.modern-snackbar {
	backdrop-filter: blur(10px);
}

/* Styles for Debt Summary Dialog */
.error-gradient {
	background: linear-gradient(135deg, #ff6b6b 0%, #ee5253 100%);
}

.payer-card {
	border: 1px solid rgba(255, 107, 107, 0.2);
	background: rgba(255, 255, 255, 0.5);
}

.expense-item {
	border-bottom: 1px dashed rgba(0, 0, 0, 0.1);
}

.expense-item:last-child {
	border-bottom: none;
}

@media (max-width: 768px) {
	.header-content {
		flex-direction: column;
		align-items: stretch;
	}

	.search-section {
		order: -1;
	}

	.search-input {
		min-width: 100% !important;
	}

	.header-icon-title {
		justify-content: center;
		text-align: center;
	}

	.page-icon {
		width: 48px;
		height: 48px;
	}

	.members-card {
		margin: 0 -1rem;
		border-radius: 16px 16px 0 0;
	}
}

@media (max-width: 600px) {
	.page-header {
		margin-bottom: 1.5rem;
	}

	.page-title {
		font-size: 1.5rem;
	}

	.dialog-card {
		margin: 1rem;
		max-width: calc(100vw - 2rem) !important;
	}

	.form-section {
		padding: 0.75rem;
	}

	.table-container {
		overflow-x: auto;
	}

	.modern-table :deep(.v-data-table__wrapper) {
		min-width: 600px;
	}
}

/* Loading states */
.modern-table :deep(.v-data-table-progress th) {
	border: none !important;
}

.modern-table :deep(.v-data-table__tr--loading) {
	height: 200px;
}

/* Form validation animations */
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

/* Success state for forms */
:deep(.v-field--success) {
	border-color: rgba(81, 207, 102, 0.5) !important;
}

/* Custom scrollbar for table */
.table-container::-webkit-scrollbar {
	height: 6px;
}

.table-container::-webkit-scrollbar-thumb {
	background: rgba(102, 126, 234, 0.3);
	border-radius: 3px;
}

.table-container::-webkit-scrollbar-track {
	background: rgba(248, 250, 252, 0.5);
	border-radius: 3px;
}
</style>
