<!--
 * @Author: 邹洋
 * @Date: 2021-07-04 13:27:27
 * @Email: 2810201146@qq.com
 * @LastEditors:  
 * @LastEditTime: 2021-10-09 10:30:24
 * @Description: 
-->
# 智慧彩云

### V 1.2.1
- 优化规则id为默认设置的id
- 解决按默认时间筛选BUG
  - BUG表现为‘刷新纪录’(刷新今天的考勤情况)功能时一直获取的是项目部署启动时候的结果，原因是这个请求不传时间时是默认获取当前时间从0点到24点，但是这个获取的方法放在了类中的Meta中所以默认时间只会在启动项目的时候加载一次，就造成了每次刷新记录的结果都一直的问题
- 导入早签接口增加可导入晨点功能
- 完善导出表格时导出晨点数据
- 修复导入签到数据日期格式问题
### V 1.2.0
- 增加功能 寝室入住 恢复
- 增加功能 寝室入住 软删除
- 考勤记录增加 被执行者学号姓名 和销假人学号姓名
- 优化excel转列表选择是否处理第一行
- 初始化系统时 创建自定义规则 的数据记录
- 优化 DormRoomInfo 当寝室没人时不在就不输出这个寝室
- 解决按默认时间筛选BUG
### V 1.1.0
- 继承User拷贝UserAdmin完成注册
- 完成自定义User移植
- 优化学生导入
- 修改默认密码为123456
- 上传学生信息时要求传递分院CodenName
- 修复权益部按照分院进行违纪搜索
- 删除任务时任务记录关于用户的地方采用默认值
- 权益部汇总统计 晚自修旷课分数修改 都不在扣2，有一个不在扣3
- 考勤规则初始化优化 实现3级规则创建
- Condition接口实现 时间区间 楼 层 3个条件的筛选
- PersonalDisciplineQuery  接口增加自己寝室扣分查询
- 设置对寝室扣分的默认名称
### V 1.0.1
- 去除重置查寝任务状态多余的重置房间的循环
- 修正SubmitKnowing 寝室考勤逻辑
  - 优化不能第二次提交的规则
- 修正撤销学生不生效问题 改为具体考勤类里面实现
### V 1.0.1
- 实现对楼层和房间按顺序排序
- 修正前端出现自定义规则这个分类
### V 1.0 
- 完成基本功能