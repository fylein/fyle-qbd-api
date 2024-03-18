from rest_framework import serializers

from .models import QBDMapping


class QBDMappingSerializer(serializers.ModelSerializer):
	class Meta:
		model = QBDMapping
		fields = '__all__'
		read_only_fields = ('workspace', 'created_at', 'updated_at')
		extra_kwargs = {
            'source_id': {
                'validators': []
            }
        }

	def create(self, validated_data):
		workspace_id = self.context['request'].parser_context.get('kwargs').get('workspace_id')

		qbd_mapping, _ = QBDMapping.objects.update_or_create(
			source_id=validated_data['source_id'],
			workspace_id=workspace_id,
			defaults={
				'destination_value': validated_data['destination_value']
			}
		)

		return qbd_mapping
