from rest_framework import serializers
from generation.models import GenerationTask, GeneratedImage


class TaskCreateSerializer(serializers.ModelSerializer):
    style_selections = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=["Fooocus V2", "Fooocus Masterpiece"]
    )
    base_model_name = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )
    performance_selection = serializers.CharField(
        required=False,
        allow_blank=True)
    aspect_ratios_selection = serializers.CharField(
        required=False,
        allow_blank=True)
    save_extension = serializers.CharField(
        required=False,
        allow_blank=True)

    class Meta:
        model = GenerationTask
        fields = (
            'prompt',
            'tg_chat_id',
            'qty',
            'style_selections',
            'base_model_name',
            'performance_selection',
            'aspect_ratios_selection',
            'save_extension',
        )

    def create(self, validated_data):
        return GenerationTask.objects.create(**validated_data)


class TaskStatusSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = GenerationTask
        fields = ("id", "status", "images")

    def get_images(self, obj):
        return GeneratedImageSerializer(obj.images.all(), many=True).data


class GeneratedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = ("index", "image")


class UserImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source='task.created_at')
    prompt = serializers.CharField(source='task.prompt', read_only=True)
    style = serializers.ListField(source='task.style_selections', read_only=True)
    model = serializers.CharField(source='task.base_model_name', read_only=True)
    performance = serializers.CharField(source='task.performance_selection', read_only=True)
    aspect = serializers.CharField(source='task.aspect_ratios_selection', read_only=True)
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedImage
        fields = (
            'url', 'created_at', 'prompt',
            'model', 'style', 'performance', 'aspect',
            'width', 'height',
        )

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)

    def get_width(self, obj):
        aspect = obj.task.aspect_ratios_selection or ''
        try:
            return int(aspect.split('*')[0])
        except (ValueError, IndexError):
            return None

    def get_height(self, obj):
        aspect = obj.task.aspect_ratios_selection or ''
        try:
            return int(aspect.split('*')[1])
        except (ValueError, IndexError):
            return None
