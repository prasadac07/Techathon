from rest_framework import serializers
from .models import UserProfile, Product, Booking,Addride, RideBooking
from django.utils import timezone

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=15, required=True)
    password = serializers.CharField(max_length=255, required=True)

    def validate_username(self, value):
        return str(value)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        image = validated_data.get("image_link", "")
        if not image:
            validated_data["image_link"] = "https://imgs.search.brave.com/hAms7Mcn0oyMfQqK0Z5RpLqQAAqAspgu5SSYdK8nOSk/rs:fit:500:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMTcz/NTgwOTMzL3Bob3Rv/L3RyYWN0b3IuanBn/P3M9NjEyeDYxMiZ3/PTAmaz0yMCZjPXR6/T1J6eHgzX3MzTm1E/ZWJQbThpMGk5TmY1/VkRONUhyVUdMMkNS/NjVZNjA9"
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance


from rest_framework.exceptions import ValidationError


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        is_accepted = instance.status == "accepted"
        lender_sign = validated_data.get("lender_sign", instance.lender_sign)
        booker_sign = validated_data.get("booker_sign", instance.booker_sign)

        if not is_accepted and (lender_sign or booker_sign):
            raise ValidationError({"message": "Cannot accept request because status is not accepted."})

        instance.lender_sign = lender_sign
        instance.booker_sign = booker_sign
        instance.save()

        return instance

class AddrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addride
        fields = '__all__'

class BookRideSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideBooking
        fields = "__all__"

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    def create(self, validated_data):
        try:
            wht = validated_data["weight_occu"]
            ride = validated_data["ride"]
            abc = Addride.objects.get(id=ride.id)
            abc.capacity -= wht
            abc.save()
        except Addride.DoesNotExist:
            # Handle the case where the associated Addride instance is not found
            raise serializers.ValidationError("Associated Addride not found.")
        except Exception as e:
            # Handle other exceptions (e.g., capacity is less than weight_occu)
            raise serializers.ValidationError(f"Error updating capacity: {str(e)}")

        instance = super().create(validated_data=validated_data)
        return instance




