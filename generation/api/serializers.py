from rest_framework import serializers

from core.services.agent import load_styles, nearest_style, generate, ALLOWED_RES
from core.services.model_alias import MODEL_ALIAS
from generation.models import GenerationTask, GeneratedImage, DailyPrompt


class TaskCreateSerializer(serializers.ModelSerializer):
    query = serializers.CharField(write_only=True)
    qty = serializers.IntegerField(required=False, min_value=1, default=1)

    class Meta:
        model = GenerationTask
        fields = (
            "query", "tg_chat_id", "qty",
            "style_selections", "base_model_name",
            "performance_selection", "aspect_ratios_selection", "save_extension",
        )
        extra_kwargs = {fld: {"required": False} for fld in (
            "style_selections", "base_model_name",
            "performance_selection", "aspect_ratios_selection", "save_extension",
        )}

    def create(self, validated_data):
        raw_query: str = validated_data.pop("query")
        agent_out = generate(raw_query)
        validated_data["prompt"] = agent_out["prompt"]
        raw_styles = agent_out["style"]
        if isinstance(raw_styles, str):
            raw_styles = [raw_styles]

        known_styles = load_styles()
        resolved = [s for s in raw_styles if s in known_styles]
        if not resolved:
            resolved.append(nearest_style(raw_query))
        validated_data["style_selections"] = resolved

        model_alias = (
            agent_out.get("model", "")
            .lower().replace(" ", "").replace("_", "-")
        )
        model_file = MODEL_ALIAS.get(model_alias)
        if model_file:
            validated_data["base_model_name"] = model_file
        else:
            validated_data.pop("base_model_name", None)

        res = str(agent_out.get("resolution", ""))
        if res in ALLOWED_RES:
            validated_data["aspect_ratios_selection"] = res
        else:
            validated_data.pop("aspect_ratios_selection", None)

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


class DailyPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrompt
        fields = ("date", "emoji", "prompt")


class QueueTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationTask
        fields = ("id", "prompt", "status", "created_at")
