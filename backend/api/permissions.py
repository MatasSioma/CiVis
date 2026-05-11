from rest_framework import permissions

from .models import User


class IsEmployer(permissions.BasePermission):
	def has_permission(self, request, view):
		return bool(
			request.user
			and request.user.is_authenticated
			and request.user.role == User.Role.EMPLOYER
		)


class IsJobSeeker(permissions.BasePermission):
	def has_permission(self, request, view):
		return bool(
			request.user
			and request.user.is_authenticated
			and request.user.role == User.Role.JOBSEEKER
		)


class IsEmployerForWrite(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True

		return bool(
			request.user
			and request.user.is_authenticated
			and request.user.role == User.Role.EMPLOYER
		)


class IsJobSeekerForWrite(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return bool(request.user and request.user.is_authenticated)

		return bool(
			request.user
			and request.user.is_authenticated
			and request.user.role == User.Role.JOBSEEKER
		)
