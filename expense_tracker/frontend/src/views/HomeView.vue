<template>
	<div>
		<div class="text-center mb-8">
			<h1 class="text-4xl font-bold text-gray-800 mb-4">
				<v-icon size="48" class="mr-3">mdi-calculator-variant</v-icon>
				Danh sách chi tiêu
			</h1>
			<p class="text-lg text-gray-600">
				Quản lý chi tiêu nhóm một cách dễ dàng
			</p>
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
					elevation="3"
					class="mb-4 hover:shadow-lg transition-shadow"
				>
					<v-card-title class="bg-primary text-white">
						<v-icon left>mdi-receipt</v-icon>
						{{ expense.name }}
					</v-card-title>

					<v-card-text class="pt-4">
						<div class="space-y-2">
							<p>
								<strong>👤 Người trả:</strong>
								{{ expense.payer.name }}
							</p>
							<p>
								<strong>💰 Tổng tiền:</strong>
								{{ formatCurrency(expense.total_amount) }}
							</p>
							<p>
								<strong>👥 Số người:</strong>
								{{ expense.participants.length }}
							</p>
							<p>
								<strong>📅 Ngày:</strong>
								{{ formatDate(expense.created_at) }}
							</p>
						</div>

						<div class="mt-4">
							<h4 class="font-semibold mb-2">
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
												? "mdi-check"
												: "mdi-clock"
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
							block
						>
							<v-icon left>mdi-eye</v-icon>
							Xem chi tiết
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
						Hãy thêm khoản chi tiêu đầu tiên của bạn
					</p>
					<v-btn
						v-if="authStore.isAuthenticated"
						to="/expenses"
						color="primary"
						size="large"
					>
						<v-icon left>mdi-plus</v-icon>
						Thêm chi tiêu
					</v-btn>
				</v-card>
			</v-col>
		</v-row>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { expensesApi } from "../services/api";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const expenses = ref([]);

const fetchExpenses = async () => {
	try {
		const response = await expensesApi.getAll();
		expenses.value = response.data;
	} catch (error) {
		console.error("Error fetching expenses:", error);
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

onMounted(fetchExpenses);
</script>
