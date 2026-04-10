from datetime import date, datetime
from typing import Any, Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class FrontBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")},
    )


class PageParams(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    limit: int = Field(10, ge=1, le=500, description="每页数量")
    sort: str = Field("", description="排序字段")
    order: str = Field("", description="排序方式")


class PageResult(FrontBaseModel, Generic[T]):
    list: List[T] = Field(default_factory=list, description="分页列表")
    count: int = Field(0, description="总数量")


class CurrentAdminUser(FrontBaseModel):
    user_id: int
    username: str
    nickname: str
    status: int


class RoleRefIn(BaseModel):
    roleId: int = Field(..., description="角色 ID")


class LoginForm(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    code: Optional[str] = Field(None, description="验证码")
    remember: bool = Field(False, description="是否记住登录态")
    tenantId: Optional[int] = Field(None, description="租户 ID")


class LoginResult(FrontBaseModel):
    access_token: str = Field(..., description="访问令牌")
    user: Optional["UserOut"] = Field(None, description="登录用户")


class CaptchaResult(FrontBaseModel):
    base64: str = Field(..., description="验证码图片")
    text: str = Field(..., description="验证码内容")


class UpdatePasswordForm(BaseModel):
    oldPassword: str = Field(..., description="旧密码")
    password: str = Field(..., description="新密码")


class UpdateUserProfileForm(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[str] = None
    email: Optional[str] = None
    introduction: Optional[str] = None
    address: Optional[str] = None
    tellPre: Optional[str] = None
    tell: Optional[str] = None


class RoleOut(FrontBaseModel):
    roleId: int
    roleCode: str
    roleName: str
    comments: Optional[str] = None
    createTime: datetime


class RoleQuery(PageParams):
    roleName: Optional[str] = None
    roleCode: Optional[str] = None


class RoleForm(BaseModel):
    roleId: Optional[int] = None
    roleCode: str
    roleName: str
    comments: Optional[str] = None


class MenuOut(FrontBaseModel):
    menuId: int
    parentId: int
    title: str
    path: str = ""
    component: Optional[str] = None
    menuType: int
    sortNumber: int = 0
    authority: Optional[str] = None
    icon: Optional[str] = None
    hide: int = 0
    meta: dict[str, Any] | str | None = None
    createTime: datetime
    children: list["MenuOut"] = Field(default_factory=list)
    openType: int = 0
    checked: Optional[bool] = None
    redirect: Optional[str] = None


class MenuQuery(PageParams):
    title: Optional[str] = None
    path: Optional[str] = None
    authority: Optional[str] = None
    parentId: Optional[int] = None


class MenuForm(BaseModel):
    menuId: Optional[int] = None
    parentId: int = 0
    title: str
    path: Optional[str] = None
    component: Optional[str] = None
    menuType: int = 0
    sortNumber: int = 0
    authority: Optional[str] = None
    icon: Optional[str] = None
    hide: int = 0
    meta: dict[str, Any] | str | None = None
    openType: int = 0
    redirect: Optional[str] = None


class OrganizationOut(FrontBaseModel):
    organizationId: int
    parentId: int
    organizationName: str
    organizationFullName: str
    organizationCode: Optional[str] = None
    organizationType: Optional[str] = None
    sortNumber: int = 0
    comments: Optional[str] = None
    createTime: datetime
    organizationTypeName: Optional[str] = None
    children: list["OrganizationOut"] = Field(default_factory=list)


class OrganizationQuery(PageParams):
    organizationName: Optional[str] = None
    organizationFullName: Optional[str] = None
    organizationType: Optional[str] = None


class OrganizationForm(BaseModel):
    organizationId: Optional[int] = None
    parentId: int = 0
    organizationName: str
    organizationFullName: str
    organizationCode: Optional[str] = None
    organizationType: Optional[str] = None
    sortNumber: int = 0
    comments: Optional[str] = None


class DictionaryOut(FrontBaseModel):
    dictId: int
    dictCode: str
    dictName: str
    sortNumber: int = 0
    comments: Optional[str] = None
    createTime: datetime


class DictionaryQuery(PageParams):
    dictCode: Optional[str] = None
    dictName: Optional[str] = None


class DictionaryForm(BaseModel):
    dictId: Optional[int] = None
    dictCode: str
    dictName: str
    sortNumber: int = 0
    comments: Optional[str] = None


class DictionaryDataOut(FrontBaseModel):
    dictDataId: int
    dictId: int
    dictDataCode: str
    dictDataName: str
    sortNumber: int = 0
    comments: Optional[str] = None
    createTime: datetime
    dictCode: Optional[str] = None


class DictionaryDataQuery(PageParams):
    keywords: Optional[str] = None
    dictDataName: Optional[str] = None
    dictDataCode: Optional[str] = None
    dictCode: Optional[str] = None
    dictId: Optional[int] = None


class DictionaryDataForm(BaseModel):
    dictDataId: Optional[int] = None
    dictId: int
    dictDataCode: str
    dictDataName: str
    sortNumber: int = 0
    comments: Optional[str] = None


class UserOut(FrontBaseModel):
    userId: int
    username: str
    password: Optional[str] = None
    nickname: str
    avatar: Optional[str] = None
    sex: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[date] = None
    introduction: Optional[str] = None
    organizationId: Optional[int] = None
    status: int = 0
    sexName: Optional[str] = None
    organizationName: Optional[str] = None
    roles: list[RoleOut] = Field(default_factory=list)
    authorities: list[MenuOut] = Field(default_factory=list)
    createTime: datetime
    address: Optional[str] = None
    tellPre: Optional[str] = None
    tell: Optional[str] = None


class UserQuery(PageParams):
    username: Optional[str] = None
    nickname: Optional[str] = None
    sex: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[int] = None
    organizationId: Optional[int] = None
    email: Optional[str] = None
    createTimeStart: Optional[str] = None
    createTimeEnd: Optional[str] = None


class UserForm(BaseModel):
    userId: Optional[int] = None
    username: str
    password: Optional[str] = None
    nickname: str
    avatar: Optional[str] = None
    sex: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    introduction: Optional[str] = None
    organizationId: Optional[int] = None
    status: int = 0
    address: Optional[str] = None
    tellPre: Optional[str] = None
    tell: Optional[str] = None
    roles: list[RoleRefIn] = Field(default_factory=list)


class UserStatusUpdateForm(BaseModel):
    userId: int
    status: int


class UserPasswordResetForm(BaseModel):
    userId: int
    password: str


class ExistenceCheckForm(BaseModel):
    field: str
    value: str
    id: Optional[int] = None


class FileRecordOut(FrontBaseModel):
    id: int
    name: str
    path: str
    length: int = 0
    contentType: Optional[str] = None
    createUserId: Optional[int] = None
    createTime: datetime
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    downloadUrl: Optional[str] = None
    createUsername: Optional[str] = None
    createNickname: Optional[str] = None


class FileRecordQuery(PageParams):
    name: Optional[str] = None
    path: Optional[str] = None
    createNickname: Optional[str] = None


class UserFileOut(FrontBaseModel):
    id: int
    userId: int
    name: str
    isDirectory: int
    parentId: int
    path: Optional[str] = None
    length: int = 0
    contentType: Optional[str] = None
    createTime: datetime
    updateTime: datetime
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    downloadUrl: Optional[str] = None


class UserFileQuery(PageParams):
    name: Optional[str] = None
    isDirectory: Optional[int] = None
    parentId: Optional[int] = None


class UserFileForm(BaseModel):
    id: Optional[int] = None
    userId: Optional[int] = None
    name: Optional[str] = None
    isDirectory: Optional[int] = None
    parentId: Optional[int] = None
    path: Optional[str] = None
    length: Optional[int] = None
    contentType: Optional[str] = None


class LoginRecordOut(FrontBaseModel):
    id: int
    username: Optional[str] = None
    os: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    ip: Optional[str] = None
    loginType: int
    comments: Optional[str] = None
    createTime: datetime
    nickname: Optional[str] = None


class LoginRecordQuery(PageParams):
    username: Optional[str] = None
    nickname: Optional[str] = None
    createTimeStart: Optional[str] = None
    createTimeEnd: Optional[str] = None
    loginType: Optional[int] = None


class OperationRecordOut(FrontBaseModel):
    id: str
    userId: Optional[int] = None
    module: str = ""
    description: str = ""
    url: str = ""
    requestMethod: str = ""
    method: str = ""
    params: str = ""
    result: str = ""
    error: str = ""
    spendTime: int = 0
    os: str = ""
    device: str = ""
    browser: str = ""
    ip: str = ""
    status: int = 0
    createTime: datetime
    nickname: str = ""
    username: str = ""


class OperationRecordQuery(PageParams):
    username: Optional[str] = None
    module: Optional[str] = None
    createTimeStart: Optional[str] = None
    createTimeEnd: Optional[str] = None
    status: Optional[int] = None


class UserMessageOut(FrontBaseModel):
    id: int
    messageType: Literal["notice", "letter", "todo"]
    title: str
    time: datetime
    status: int
    content: Optional[str] = None
    avatar: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class UserMessageQuery(PageParams):
    messageType: Literal["notice", "letter", "todo"]
    title: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[int] = None


class UserMessageUnread(FrontBaseModel):
    notices: list[UserMessageOut] = Field(default_factory=list)
    letters: list[UserMessageOut] = Field(default_factory=list)
    todos: list[UserMessageOut] = Field(default_factory=list)


class UserMessageStatusUpdateForm(BaseModel):
    messageType: Literal["notice", "letter", "todo"]
    ids: list[int] = Field(default_factory=list)


class UserMessageRemoveForm(BaseModel):
    ids: list[int] = Field(default_factory=list)


UserOut.model_rebuild()
LoginResult.model_rebuild()
MenuOut.model_rebuild()
OrganizationOut.model_rebuild()
