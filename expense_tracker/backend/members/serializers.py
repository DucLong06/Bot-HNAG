from rest_framework import serializers
from .models import Member, MemberGroup


class MemberSerializer(serializers.ModelSerializer):
    """Base serializer - hides telegram_id from non-admin users"""
    class Meta:
        model = Member
        fields = ['id', 'name', 'bank_name', 'account_number', 'created_at']


class MemberWriteSerializer(serializers.ModelSerializer):
    """Write serializer - accepts telegram_id for create/update but hides it in response"""
    class Meta:
        model = Member
        fields = ['id', 'name', 'telegram_id', 'bank_name', 'account_number', 'created_at']
        extra_kwargs = {'telegram_id': {'write_only': True}}


class MemberAdminSerializer(serializers.ModelSerializer):
    """Admin serializer - shows telegram_id"""
    class Meta:
        model = Member
        fields = ['id', 'name', 'telegram_id', 'bank_name', 'account_number', 'created_at']


class MemberGroupSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    is_owner = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MemberGroup
        fields = ['id', 'name', 'members', 'member_ids', 'created_at', 'is_owner', 'created_by_name']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            if obj.created_by is None:
                return request.user.is_superuser
            return obj.created_by == request.user or request.user.is_superuser
        return False

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        group = MemberGroup.objects.create(**validated_data)
        if member_ids:
            group.members.set(member_ids)
        return group

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if member_ids is not None:
            instance.members.set(member_ids)
        return instance
