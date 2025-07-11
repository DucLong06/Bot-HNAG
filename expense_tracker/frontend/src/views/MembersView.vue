<template>
	<div>
		<div class="flex justify-between items-center mb-6">
			<div>
				<h1 class="text-3xl font-bold text-gray-800">
					<v-icon size="32" class="mr-2">mdi-account-group</v-icon>
					Quản lý thành viên
				</h1>
				<p class="text-gray-600 mt-2">
					Quản lý danh sách thành viên tham gia chi tiêu
				</p>
			</div>
			<v-btn color="primary" @click="openAddDialog" size="large">
				<v-icon left>mdi-plus</v-icon>
				Thêm thành viên
			</v-btn>
		</div>

		<v-card elevation="2">
			<v-card-title class="d-flex align-center pe-2">
				<v-icon icon="mdi-account-multiple"></v-icon> &nbsp; Danh sách
				thành viên
				<v-spacer></v-spacer>
				<v-text-field
					v-model="search"
					density="compact"
					label="Tìm kiếm"
					prepend-inner-icon="mdi-magnify"
					variant="solo-filled"
					flat
					hide-details
					single-line
				></v-text-field>
			</v-card-title>

			<v-data-table
				:headers="headers"
				:items="members"
				:search="search"
				class="elevation-0"
				:loading="loading"
				loading-text="Đang tải dữ liệu..."
				no-data-text="Không có dữ liệu"
			>
				<template v-slot:item.created_at="{ item }">
					{{ formatDate(item.created_at) }}
				</template>

				<template v-slot:item.actions="{ item }">
					<v-btn
						icon="mdi-pencil"
						size="small"
						color="orange"
						variant="text"
						@click="editMember(item)"
					></v-btn>
					<v-btn
						icon="mdi-delete"
						size="small"
						color="red"
						variant="text"
						@click="deleteMember(item)"
					></v-btn>
				</template>
			</v-data-table>
		</v-card>

		<!-- Add/Edit Dialog -->
		<v-dialog v-model="dialog" max-width="500px" persistent>
			<v-card>
				<v-card-title class="bg-primary text-white">
					<v-icon left>{{
						editedIndex === -1 ? "mdi-plus" : "mdi-pencil"
					}}</v-icon>
					{{
						editedIndex === -1
							? "Thêm thành viên mới"
							: "Sửa thành viên"
					}}
				</v-card-title>

				<v-card-text class="pt-6">
					<v-form ref="form" v-model="valid">
						<v-text-field
							v-model="editedItem.name"
							label="Tên thành viên"
							variant="outlined"
							:rules="[(v) => !!v || 'Tên là bắt buộc']"
							required
							prepend-inner-icon="mdi-account"
						></v-text-field>

						<v-text-field
							v-model="editedItem.telegram_id"
							label="Telegram ID"
							variant="outlined"
							:rules="[(v) => !!v || 'Telegram ID là bắt buộc']"
							required
							prepend-inner-icon="mdi-telegram"
							hint="ID Telegram để gửi nhắc nhở"
							persistent-hint
						></v-text-field>
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
						:disabled="!valid"
						:loading="saving"
					>
						<v-icon left>mdi-check</v-icon>
						Lưu
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<!-- Delete Confirmation -->
		<v-dialog v-model="deleteDialog" max-width="400px">
			<v-card>
				<v-card-title class="text-h5 bg-red text-white">
					<v-icon left>mdi-delete</v-icon>
					Xác nhận xóa
				</v-card-title>
				<v-card-text class="pt-4">
					Bạn có chắc muốn xóa thành viên
					<strong>{{ memberToDelete?.name }}</strong
					>? <br /><br />
					<v-alert type="warning" variant="tonal">
						Hành động này không thể hoàn tác!
					</v-alert>
				</v-card-text>
				<v-card-actions>
					<v-spacer></v-spacer>
					<v-btn
						color="grey"
						variant="outlined"
						@click="deleteDialog = false"
						>Hủy</v-btn
					>
					<v-btn
						color="red"
						@click="confirmDelete"
						:loading="deleting"
						>Xóa</v-btn
					>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { membersApi } from "../services/api";

const search = ref("");
const dialog = ref(false);
const deleteDialog = ref(false);
const valid = ref(false);
const loading = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editedIndex = ref(-1);
const members = ref([]);
const memberToDelete = ref(null);

const headers = [
	{ title: "Tên", key: "name" },
	{ title: "Telegram ID", key: "telegram_id" },
	{ title: "Ngày tạo", key: "created_at" },
	{ title: "Hành động", key: "actions", sortable: false },
];

const editedItem = ref({
	name: "",
	telegram_id: "",
});

const defaultItem = {
	name: "",
	telegram_id: "",
};

const fetchMembers = async () => {
	loading.value = true;
	try {
		const response = await membersApi.getAll();
		members.value = response.data;
	} catch (error) {
		console.error("Error fetching members:", error);
	} finally {
		loading.value = false;
	}
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
	} catch (error) {
		console.error("Error deleting member:", error);
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
		} else {
			await membersApi.create(editedItem.value);
		}
		await fetchMembers();
		close();
	} catch (error) {
		console.error("Error saving member:", error);
	} finally {
		saving.value = false;
	}
};

const formatDate = (dateString: string) => {
	return new Date(dateString).toLocaleDateString("vi-VN");
};

onMounted(fetchMembers);
</script>
