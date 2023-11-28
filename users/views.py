from django.utils import timezone

from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .serializers import SignupSerializer, LoginSerializer, MyPageSerializer


class SignUpView(APIView):
    """
    POST : 회원가입
    """

    def get(self, request):
        return Response({"message": "username, name, password를 입력해주세요."})

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user_pk": user.pk,
                    "name": user.name,
                    "username": user.username,
                    "message": "회원가입이 완료되었습니다.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST : 로그인
    """

    def get(self, request):
        return Response({"message": "username, password를 입력해주세요."})

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if username is None or password is None:
            return Response(
                {"message": "username, password를 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            serializer = LoginSerializer(user)

            # simple jwt 토큰 발급
            token = TokenObtainPairSerializer.get_token(user)
            access_token = str(token.access_token)
            refresh_token = str(token)

            res = Response(
                {
                    "user_pk": user.pk,
                    "username": user.username,
                    "message": f"{user.name}님, 로그인이 완료되었습니다.",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

            request.session["refresh_token"] = refresh_token
            res.set_cookie("access_token", access_token, httponly=True)

            return res
        else:
            return Response(
                {"message": "아이디 또는 비밀번호가 일치하지 않습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    """
    POST : 로그아웃
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "로그아웃 하시겠습니까?"})

    def post(self, request):
        # 쿠키에서 access_token 삭제
        response = Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")

        # 세션에서 refresh_token 가져오기
        refresh_token = request.session.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                del request.session["refresh_token"]
            except Exception as e:
                print(e)

            return response

        logout(request)
        return response


class MyPageView(APIView):
    """
    GET : 내 정보 조회
    PUT : 내 정보 수정
    DELETE : 회원 탈퇴
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = MyPageSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = MyPageSerializer(
            user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            updated_info = serializer.save()
            return Response(
                MyPageSerializer(updated_info).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "계정이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
