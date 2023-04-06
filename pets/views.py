from rest_framework.views import APIView, Response, Request, status
from pets.serializers import PetSerializer
from groups.models import Group
from pets.models import Pet
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group")
        traits_data = serializer.validated_data.pop("traits")

        group_found = Group.objects.filter(
            scientific_name__iexact=group_data["scientific_name"]
        ).first()

        if not group_found:
            group_found = Group.objects.create(**group_data)

        pet_obj = Pet.objects.create(**serializer.validated_data, group=group_found)

        for trait in traits_data:
            trait_found = Trait.objects.filter(name__iexact=trait["name"]).first()

            if not trait_found:
                trait_found = Trait.objects.create(**trait)

            pet_obj.traits.add(trait_found)

        serializer = PetSerializer(pet_obj)

        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        req_param = request.query_params.get("trait")

        if req_param:
            pets = Pet.objects.filter(traits__name__iexact=req_param)
        else:
            pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request)

        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def patch(self, request: Request, pet_id: int):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        group_data: dict = serializer.validated_data.pop("group", None)
        traits_data = serializer.validated_data.pop("traits", None)

        if group_data:
            group_found = Group.objects.filter(
                scientific_name__iexact=group_data["scientific_name"]
            ).first()

            if not group_found:
                group_found = Group.objects.create(**group_data)

            pet.group = group_found
            pet.save()

        if traits_data:
            new_traits = []

            for trait in traits_data:
                trait_found = Trait.objects.filter(name__iexact=trait["name"]).first()

                if not trait_found:
                    trait_found = Trait.objects.create(**trait)

                new_traits.append(trait_found)

            pet.traits.set(new_traits)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
