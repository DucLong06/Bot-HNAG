<template>
	<div>
		<div class="flex justify-between items-center mb-6">
			<div>
				<h1 class="text-3xl font-bold text-gray-800">
					<v-icon size="32" class="mr-2">mdi-credit-card</v-icon>
					Quản lý chi tiêu
				</h1>
				<p class="text-gray-600 mt-2">
					Tạo và quản lý các khoản chi tiêu nhóm
				</p>
			</div>
			<v-btn color="primary" @click="openAddDialog" size="large">
				<v-icon left>mdi-plus</v-icon>
				Thêm khoản chi tiêu
			</v-btn>
		</div>

		<v-row v-if="expenses.length > 0">
			<v-col
				v-for="expense in expenses"
				:key="expense.id"
				cols="12"
				md="6"
				lg="4"
			>
				<v-card
					class="mb-4 hover:shadow-lg transition-shadow"
					elevation="2"
				>
					<v-card-title
						class="bg-gradient-to-r from-blue-500 to-blue-600 text-white"
					>
						<v-icon left>mdi-receipt</v-icon>
						{{ expense.name }}
					</v-card-title>

					<v-card-text class="pt-4">
						<div class="space-y-3">
							<div class="flex items-center">
								<v-icon color="green" class="mr-2"
									>mdi-account-cash</v-icon
								>
								<span
									><strong>Người trả:</strong>
									{{ expense.payer.name }}</span
								>
							</div>

							<div class="flex items-center">
								<v-icon color="primary" class="mr-2"
									>mdi-currency-usd</v-icon
								>
								<span
									><strong>Tổng tiền:</strong>
									{{
										formatCurrency(expense.total_amount)
									}}</span
								>
							</div>

							<div class="flex items-center">
								<v-icon color="orange" class="mr-2"
									>mdi-account-group</v-icon
								>
								<span
									><strong>Số người:</strong>
									{{ expense.participants.length }}</span
								>
							</div>

							<div class="flex items-center">
								<v-icon color="purple" class="mr-2"
									>mdi-calendar</v-icon
								>
								<span
									><strong>Ngày:</strong>
									{{ formatDate(expense.created_at) }}</span
								>
							</div>
						</div>

						<v-divider class="my-4"></v-divider>

						<div>
							<h4 class="font-semibold mb-2 flex items-center">
								<v-icon small class="mr-1"
									>mdi-chart-pie</v-icon
								>
								Trạng thái thanh toán:
							</h4>
							<div class="flex flex-wrap gap-1">
								<v-chip
									v-for="participant in expense.participants"
									:key="participant.id"
									:color="
										participant.is_paid
											? 'success'
											: 'error'
									"
									size="small"
									class="mb-1"
								>
									<v-icon left size="small">
										{{
											participant.is_paid
												? "mdi-check-circle"
												: "mdi-clock-outline"
										}}
									</v-icon>
									{{ participant.member.name }}
								</v-chip>
							</div>
						</div>
					</v-card-text>

					<v-card-actions>
						<v-btn
							:to="`/expenses/${expense.id}`"
							color="primary"
							variant="outlined"
							size="small"
						>
							<v-icon left>mdi-eye</v-icon>
							Chi tiết
						</v-btn>

						<v-btn
							@click="editExpense(expense)"
							color="orange"
							variant="outlined"
							size="small"
						>
							<v-icon left>mdi-pencil</v-icon>
							Sửa
						</v-btn>

						<v-btn
							@click="deleteExpense(expense)"
							color="red"
							variant="outlined"
							size="small"
						>
							<v-icon left>mdi-delete</v-icon>
							Xóa
						</v-btn>
					</v-card-actions>
				</v-card>
			</v-col>
		</v-row>

		<v-row v-else>
			<v-col cols="12">
				<v-card class="text-center pa-8">
					<v-icon size="64" color="grey-lighten-1"
						>mdi-receipt-text-outline</v-icon
					>
					<h3 class="text-xl mt-4 mb-2">
						Chưa có khoản chi tiêu nào
					</h3>
					<p class="text-gray-600 mb-4">
						Hãy tạo khoản chi tiêu đầu tiên
					</p>
				</v-card>
			</v-col>
		</v-row>

		<!-- Add/Edit Dialog -->
		<v-dialog v-model="dialog" max-width="900px" persistent>
			<v-card>
				<v-card-title class="bg-primary text-white">
					<v-icon left>{{
						editedIndex === -1 ? "mdi-plus" : "mdi-pencil"
					}}</v-icon>
					{{
						editedIndex === -1
							? "Thêm khoản chi tiêu mới"
							: "Sửa khoản chi tiêu"
					}}
				</v-card-title>

				<v-card-text class="pt-6">
					<v-form ref="form" v-model="valid">
						<v-row>
							<v-col cols="12" md="6">
								<v-text-field
									v-model="editedItem.name"
									label="Tên khoản chi tiêu"
									variant="outlined"
									:rules="[(v) => !!v || 'Tên là bắt buộc']"
									required
									prepend-inner-icon="mdi-receipt"
								></v-text-field>
							</v-col>

							<v-col cols="12" md="6">
								<v-text-field
									v-model.number="editedItem.total_amount"
									label="Tổng số tiền (VND)"
									type="number"
									variant="outlined"
									:rules="[
										(v) => !!v || 'Số tiền là bắt buộc',
										(v) =>
											v > 0 || 'Số tiền phải lớn hơn 0',
									]"
									required
									prepend-inner-icon="mdi-currency-usd"
								></v-text-field>
							</v-col>

							<v-col cols="12">
								<v-select
									v-model="editedItem.payer_id"
									:items="members"
									item-title="name"
									item-value="id"
									label="Người trả tiền"
									variant="outlined"
									:rules="[
										(v) => !!v || 'Người trả là bắt buộc',
									]"
									required
									prepend-inner-icon="mdi-account-cash"
								></v-select>
							</v-col>
						</v-row>

						<v-divider class="my-6"></v-divider>

						<div class="flex justify-between items-center mb-4">
							<h3 class="text-lg font-semibold">
								Người tham gia
							</h3>
							<div class="space-x-2">
								<v-btn
									@click="distributeEvenly"
									size="small"
									color="success"
									variant="outlined"
								>
									<v-icon left>mdi-calculator</v-icon>
									Chia đều
								</v-btn>
								<v-btn
									@click="addParticipant"
									color="primary"
									size="small"
								>
									<v-icon left>mdi-plus</v-icon>
									Thêm người
								</v-btn>
							</div>
						</div>

						<v-alert v-if="totalError" type="error" class="mb-4">
							<v-icon left>mdi-alert-circle</v-icon>
							Tổng tiền người tham gia ({{
								formatCurrency(participantTotal)
							}}) phải bằng tổng số tiền ({{
								formatCurrency(editedItem.total_amount)
							}})
						</v-alert>

						<div
							v-if="editedItem.participant_data.length === 0"
							class="text-center py-4"
						>
							<v-icon size="48" color="grey-lighten-1"
								>mdi-account-plus</v-icon
							>
							<p class="text-grey-lighten-1 mt-2">
								Chưa có người tham gia nào
							</p>
						</div>

						<v-row
							v-for="(
								participant, index
							) in editedItem.participant_data"
							:key="index"
							class="mb-2"
						>
							<v-col cols="12" md="5">
								<v-select
									v-model="participant.member_id"
									:items="members"
									item-title="name"
									item-value="id"
									label="Chọn thành viên"
									variant="outlined"
									density="compact"
								></v-select>
							</v-col>
							<v-col cols="12" md="4">
								<v-text-field
									v-model.number="participant.amount_owed"
									type="number"
									label="Số tiền (VND)"
									variant="outlined"
									density="compact"
								></v-text-field>
							</v-col>
							<v-col cols="12" md="2">
								<v-checkbox
									v-model="participant.is_paid"
									label="Đã trả"
									hide-details
								></v-checkbox>
							</v-col>
							<v-col cols="12" md="1">
								<v-btn
									@click="removeParticipant(index)"
									size="small"
									color="red"
									icon
									variant="outlined"
								>
									<v-icon>mdi-delete</v-icon>
								</v-btn>
							</v-col>
						</v-row>
					</v-form>
				</v-card-text>

				<v-card-actions class="pa-4">
					<v-spacer></v-spacer>
					<v-btn color="grey" variant="outlined" @click="close">
						<v-icon left>mdi-close</v-icon>
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
					>
						<v-icon left>mdi-check</v-icon>
						Lưu
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { expensesApi, membersApi } from "../services/api";

const dialog = ref(false);
const valid = ref(false);
const saving = ref(false);
const editedIndex = ref(-1);
const expenses = ref([]);
const members = ref([]);

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

const fetchExpenses = async () => {
	try {
		const response = await expensesApi.getAll();
		expenses.value = response.data;
	} catch (error) {
		console.error("Error fetching expenses:", error);
	}
};

const fetchMembers = async () => {
	try {
		const response = await membersApi.getAll();
		members.value = response.data;
	} catch (error) {
		console.error("Error fetching members:", error);
	}
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
		} catch (error) {
			console.error("Error deleting expense:", error);
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
		} else {
			await expensesApi.create(editedItem.value);
		}
		await fetchExpenses();
		close();
	} catch (error) {
		console.error("Error saving expense:", error);
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
