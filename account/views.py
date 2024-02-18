from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserProfile, Product, Booking
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Booking, Product,Addride, RideBooking
from .serializers import UserProfileSerializer, LoginSerializer, ProductSerializer, BookingSerializer,AddrideSerializer, BookRideSerializer
from django.middleware import csrf
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model
import logging
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)
User = get_user_model()

# class gettoken(APIView):
#     def post(self, request):
#         data = request.data
#
#         if 'mobile' in data:
#             token = get

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        # print(serializer.validated_data, username, password)
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        logger.debug(f"Attempting login for user: {username}")

        if user:
            user.save()

            # expiration_time = datetime.now() + timedelta(seconds=20)

            token_obj, _ = Token.objects.get_or_create(user=user)
            # token_obj.expires_at = expiration_time
            token_obj.save()

            response = Response({'message': 'Login successful', "token": str(token_obj)}, status=status.HTTP_200_OK)

            response['Authorization'] = "token " + str(token_obj)
            response.set_cookie('token', str(token_obj), max_age=None, httponly=True)

            return response
        else:
            return Response({"messege": "error"}, status=status.HTTP_400_BAD_REQUEST)




class LogoutView(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.COOKIES.get('token')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        # For example, you can access the user associated with the token
        user = token_obj.user
        # Get the user associated with the token

        # Delete the existing token for the user
        Token.objects.filter(user=user).delete()
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        for cookie_name in request.COOKIES.keys():
            response.delete_cookie(cookie_name)

        return response

class RegisterUserView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)



class InformationProduct(APIView):
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):

        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        # For example, you can access the user associated with the token
        user = token_obj.user
        # user = UserProfile.objects.get(id=4)
        data = request.data
        # user = UserProfile.objects.get(id = 3)
        # if request.META.get('HTTP_CONTENT_TYPE'):
        #     print(request.META.get('HTTP_CONTENT_TYPE'))
        # print(request.META)
        # for key, value in request.META.items():
        #     if key.startswith('HTTP'):
        #         print(f"{key}: {value}")



        # image = "https://imgs.search.brave.com/hAms7Mcn0oyMfQqK0Z5RpLqQAAqAspgu5SSYdK8nOSk/rs:fit:500:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMTcz/NTgwOTMzL3Bob3Rv/L3RyYWN0b3IuanBn/P3M9NjEyeDYxMiZ3/PTAmaz0yMCZjPXR6/T1J6eHgzX3MzTm1E/ZWJQbThpMGk5TmY1/VkRONUhyVUdMMkNS/NjVZNjA9"

        if 'image_link' not in data or data["image_link"] == "":
            image = "n7fluvteh4df1x0vfegq"
        else:
            image = data["image_link"]

        payload = {
                "available_till": data["available_till"],
                "ask_price": data["ask_price"],
            "image_link": image,
            "pincode": data["pincode"],
                "description": data["description"],
                "from_user": user.id,
                "available_from": data["available_from"],
                "product_type": data["product_type"],
                "company_name": data["company_name"],
                "taluka": data["taluka"]
            }


        # print(payload)
        ser = ProductSerializer(data=payload)

        if ser.is_valid():
            ser.save()
            return Response({"messege": "product created"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"messege": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        # For example, you can access the user associated with the token
        user = token_obj.user
        prdt = Product.objects.exclude(from_user=user).order_by('-id')

        ser = ProductSerializer(prdt, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class getall(APIView):
    def get(self, request):
        prdt = Product.objects.all().order_by('-id')
        ser = ProductSerializer(prdt, many=True)
        print(UserProfile.objects.get(username=8888899999).id)
        return Response(ser.data, status=status.HTTP_200_OK)




class BookProduct(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):

        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        # For example, you can access the user associated with the token
        user = token_obj.user

        prdtid = request.data["id"]
        num_hrs = int(request.data["hours"])
        # user = UserProfile.objects.get(id = 4)

        product = Product.objects.get(id = int(prdtid))
        # user_id = request.data["user_id"]

        userr = UserProfile.objects.get(username = product.from_user)
        print(user.id, userr.id)

        if 'status' in request.data and request.data["status"]:
            stattus = request.data["status"]
        else:
            stattus = "pending"

        if user.id != userr.id:
            payload = {
                    "product": prdtid,
                    "asker": user.id,
                    "status": stattus,
                    "number_of_hours": num_hrs,
                    "when_date": request.data["date"]
                }
            ser = BookingSerializer(data=payload)
            if ser.is_valid():
                    ser.save()
                    return Response({"messege": "booking successfull", "data": ser.data}, status=status.HTTP_200_OK)
            else:
                    return Response({"messege": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"messege": "cannot book your own item"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateBookingStatus(APIView):
    def put(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            print("no token")
            return Response({'error': 'Token not found in headers'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        user = token_obj.user

        data = request.data

        if "id" not in request.data:
            print("no id")
            return Response({"messege": "error"}, status=status.HTTP_404_NOT_FOUND)


        booking = Booking.objects.get(id=str(request.data["id"]))

        if not booking:
            print("problem")
            return Response({"..": ".."})

        if "status" not in request.data:
            print("no changeeee")
            return Response({"no change": "no change"})

        booking.status = data.get("status")
        booking.save()

        serializer = BookingSerializer(instance=booking)
        return Response({"message": "Status changed", "data": serializer.data}, status=status.HTTP_200_OK)



class CheckBooking(APIView):
    def get(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in headers'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        # For example, you can access the user associated with the token
        user = token_obj.user

        # Fetch bookings associated with the user
        booking_objs = Booking.objects.filter(asker=user)

        # Serialize the booking objects
        ser = BookingSerializer(booking_objs, many=True)
        payload = ser.data
        for p in payload:
            prdt = Product.objects.get(id= int(p["product"]))
            p["price"] = float(float(p["number_of_hours"])*prdt.ask_price)
            p["equipement_type"] = str(prdt.product_type)
        # Check if any bookings were found
        if not booking_objs:
            return Response({"message": "No bookings found for this user"}, status=status.HTTP_404_NOT_FOUND)

        # Return the serialized data
        return Response(ser.data, status=status.HTTP_200_OK)


class CheckRequests(APIView):
    def get(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in headers'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        # For example, you can access the user associated with the token
        user = token_obj.user

        # Get the user's products
        user_products = Product.objects.filter(from_user=user)

        # Use the user's products to filter the bookings
        booking = Booking.objects.filter(product__in=user_products).order_by('-id')

        ser = BookingSerializer(booking, many=True)
        payload = ser.data
        for p in payload:
            prdt = Product.objects.get(id= int(p["product"]))
            p["price"] = float(float(p["number_of_hours"])*prdt.ask_price)
            p["equipement_type"] = str(prdt.product_type)


        return Response(payload, status=status.HTTP_200_OK)




class InformationAddride(APIView):
    def post(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        user = token_obj.user

        # Check if the user is a driver
        # if not user.driver:
        #     return Response({"message": "Only drivers are allowed to post a ride"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        print(user.id, str(token_obj))

        payload = {
            "from_user": user.id,
            "driver_name": data["driver_name"],
            "vehicle_name": data["vehicle_name"],
            "location_from": data["location_from"],
            "location_to": data["location_to"],
            "available_on": data["available_on"],
            "departure_time": data["departure_time"],
            "price_ton": data["price_ton"],
            "capacity": data["capacity"],
            "specifications": data["specifications"]
        }

        ser = AddrideSerializer(data=payload)

        if ser.is_valid():
            ser.save()
            return Response({"message": "Ride Added"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
        
        user = token_obj.user
        prdt = Addride.objects.exclude(from_user=user).order_by('-id')

        ser = AddrideSerializer(prdt, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class BookRide(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):

        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Token is valid, continue processing the request
        # For example, you can access the user associated with the token
        user = token_obj.user

        # payload_keys = {'id', 'weight'}
        # if not payload_keys.issubset(request.data.keys()):
        #     return Response({"message": f"Invalid payload. Required keys: {payload_keys}"}, status=status.HTTP_400_BAD_REQUEST)

        ride_id = int(request.data["id"])
        weight = float(request.data["weight"])

        # try:
        #     ride_id = int(ride_id)
        # except (ValueError, TypeError):
        #     return Response({"message": "Invalid 'id' in the payload"}, status=status.HTTP_400_BAD_REQUEST)

        ride = Addride.objects.get(id=ride_id)

        if ride.capacity < weight:
            return Response({"message": "Cannot book this ride"}, status=status.HTTP_400_BAD_REQUEST)

        owner = UserProfile.objects.get(username=ride.from_user)

        if owner.id == user.id:
            return Response({"message": "You cannot book your own ride"}, status=status.HTTP_400_BAD_REQUEST)

        existing_booking = RideBooking.objects.filter(ride=ride.id, asker=user.id).first()

        if existing_booking:
            return Response({"message": "You have already booked the ride"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "ride": ride.id,
            "asker": user.id,
            "weight_occu": weight,
            "ride_confirm": False
        }
        print(payload)
        serializer = BookRideSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Booking successful", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    # def get(self, request):
    #     user = request.user
    #


class ShowRideBookings(APIView):
    def get(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in headers'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        user = token_obj.user

        # Check if the user is a driver
        # if user.driver:
        #     return Response({"message": "Drivers are not allowed to view bookings"}, status=status.HTTP_403_FORBIDDEN)

        # Fetch bookings associated with the user
        booking_objs = RideBooking.objects.filter(asker=user.id)

        # Serialize the booking objects
        ser = BookRideSerializer(booking_objs, many=True)

        # Check if any bookings were found
        if not booking_objs:
            return Response({"message": "No bookings found for this user"}, status=status.HTTP_404_NOT_FOUND)

        # Return the serialized data
        return Response(ser.data, status=status.HTTP_200_OK) 

class ShowPeopleBooking(APIView):
    def get(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in headers'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        user = token_obj.user

        # if not user.driver:
        #     return Response({"message": "You are not a driver"}, status=status.HTTP_403_FORBIDDEN)

        user_rides = Addride.objects.filter(from_user=user)
        booking = RideBooking.objects.filter(ride__in=user_rides).order_by('-id')

        ser = BookRideSerializer(booking, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class UpdateRideBookingStatus(APIView):
    def put(self, request, pk):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            return Response({'error': 'Token not found in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the token
        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        user = token_obj.user

        try:
            booking = RideBooking.objects.get(id=pk)
        except RideBooking.DoesNotExist:
            return Response({'error': 'RideBooking not found'}, status=status.HTTP_404_NOT_FOUND)
# Check if the user is a driver
#         if not user.driver:
#             return Response({'error': 'Only drivers are allowed to update the RideBooking status.'}, status=status.HTTP_403_FORBIDDEN)

        # if booking.asker != user:
        #     return Response({'error': 'You do not have permission to update this RideBooking'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        if 'ride_confirm' in data:
            new_status = data['ride_confirm'].lower()
            if new_status in ['accepted', 'rejected']:
                booking.ride_confirm = new_status
                booking.save()

                ser = BookRideSerializer(instance=booking)
                return Response({"message": f'The request has been {new_status}', "data": ser.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid value for 'ride_confirm'. It should be 'accepted' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "The 'ride_confirm' field is required for updating the status."}, status=status.HTTP_400_BAD_REQUEST)
  




