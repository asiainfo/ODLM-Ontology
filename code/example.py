from core.ontology import OntologyService

ontology_client = OntologyService()

# 创建一个用户，如果没有的话
ontology_client.create_instance(
  object_name="Tom",
  object_class="User",
  properties={
  }
)

# 创建非Object映射的表和字段实例

# 1) 创建 tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info 表
ontology_client.create_instance(
  object_name="tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info",
  object_class="Table",
  properties={
    "tableId": "tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info",
    "belongsToDataSource": "test_db",
    "owner": "Tom"
  }
)

# tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info 表的主要字段
ontology_client.create_instance(
  object_name="tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info_ec_group_cust_code",
  object_class="Field",
  properties={
    "fieldId": "EC_GROUP_CUST_CODE",
    "dataType": "varchar(20)",
    "isNullable": True,
    "belongsToTable": "tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info"
  }
)

ontology_client.create_instance(
  object_name="tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info_comdt_specs_code",
  object_class="Field",
  properties={
    "fieldId": "COMDT_SPECS_CODE",
    "dataType": "varchar(20)",
    "isNullable": True,
    "belongsToTable": "tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info"
  }
)

ontology_client.create_instance(
  object_name="tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info_ord_tm",
  object_class="Field",
  properties={
    "fieldId": "ORD_TM",
    "dataType": "datetime",
    "isNullable": True,
    "belongsToTable": "tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info"
  }
)

ontology_client.create_instance(
  object_name="tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info_eff_date",
  object_class="Field",
  properties={
    "fieldId": "EFF_DATE",
    "dataType": "date",
    "isNullable": True,
    "belongsToTable": "tb_d_svc_is_a45034_unitntw_cust_comdt_ord_base_info"
  }
)

# 2) 创建 to_d_pty_cm_a45014_headquat_cust_info 表
ontology_client.create_instance(
  object_name="to_d_pty_cm_a45014_headquat_cust_info",
  object_class="Table",
  properties={
    "tableId": "to_d_pty_cm_a45014_headquat_cust_info",
    "belongsToDataSource": "test_db",
    "owner": "Tom"
  }
)

# to_d_pty_cm_a45014_headquat_cust_info 表的主要字段
ontology_client.create_instance(
  object_name="to_d_pty_cm_a45014_headquat_cust_info_bboss_group_cust_id",
  object_class="Field",
  properties={
    "fieldId": "bboss_group_cust_id",
    "dataType": "varchar(30)",
    "isNullable": True,
    "belongsToTable": "to_d_pty_cm_a45014_headquat_cust_info"
  }
)

ontology_client.create_instance(
  object_name="to_d_pty_cm_a45014_headquat_cust_info_group_cust_name",
  object_class="Field",
  properties={
    "fieldId": "group_cust_name",
    "dataType": "varchar(30)",
    "isNullable": True,
    "belongsToTable": "to_d_pty_cm_a45014_headquat_cust_info"
  }
)

ontology_client.create_instance(
  object_name="to_d_pty_cm_a45014_headquat_cust_info_create_date",
  object_class="Field",
  properties={
    "fieldId": "create_date",
    "dataType": "varchar(30)",
    "isNullable": True,
    "belongsToTable": "to_d_pty_cm_a45014_headquat_cust_info"
  }
)

ontology_client.create_instance(
  object_name="to_d_pty_cm_a45014_headquat_cust_info_indus_type_code",
  object_class="Field",
  properties={
    "fieldId": "indus_type_code",
    "dataType": "varchar(2)",
    "isNullable": True,
    "belongsToTable": "to_d_pty_cm_a45014_headquat_cust_info"
  }
)

ontology_client.create_instance(
  object_name="to_d_pty_cm_a45014_headquat_cust_info_group_lvl_code",
  object_class="Field",
  properties={
    "fieldId": "group_lvl_code",
    "dataType": "varchar(1)",
    "isNullable": True,
    "belongsToTable": "to_d_pty_cm_a45014_headquat_cust_info"
  }
)

# 3) 创建 t_dim_n_md_h_prov_city 表
ontology_client.create_instance(
  object_name="t_dim_n_md_h_prov_city",
  object_class="Table",
  properties={
    "tableId": "t_dim_n_md_h_prov_city",
    "belongsToDataSource": "test_db",
    "owner": "Tom"
  }
)

# t_dim_n_md_h_prov_city 表的主要字段
ontology_client.create_instance(
  object_name="t_dim_n_md_h_prov_city_city_lvl",
  object_class="Field",
  properties={
    "fieldId": "city_lvl",
    "dataType": "varchar(2)",
    "isNullable": True,
    "belongsToTable": "t_dim_n_md_h_prov_city"
  }
)

ontology_client.create_instance(
  object_name="t_dim_n_md_h_prov_city_city_name",
  object_class="Field",
  properties={
    "fieldId": "city_name",
    "dataType": "varchar(50)",
    "isNullable": True,
    "belongsToTable": "t_dim_n_md_h_prov_city"
  }
)

ontology_client.create_instance(
  object_name="t_dim_n_md_h_prov_city_prov_name",
  object_class="Field",
  properties={
    "fieldId": "prov_name",
    "dataType": "varchar(40)",
    "isNullable": True,
    "belongsToTable": "t_dim_n_md_h_prov_city"
  }
)

ontology_client.create_instance(
  object_name="t_dim_n_md_h_prov_city_prov_id_3",
  object_class="Field",
  properties={
    "fieldId": "prov_id_3",
    "dataType": "varchar(3)",
    "isNullable": True,
    "belongsToTable": "t_dim_n_md_h_prov_city"
  }
)

ontology_client.create_instance(
  object_name="t_dim_n_md_h_prov_city_prov_id_5",
  object_class="Field",
  properties={
    "fieldId": "prov_id_5",
    "dataType": "varchar(5)",
    "isNullable": True,
    "belongsToTable": "t_dim_n_md_h_prov_city"
  }
)

# 创建源表
ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf",
  object_class="Table",
  properties={
    "tableId": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf",
    "belongsToDataSource": "test_db",
    "owner": "Tom"
  }
)

# tw_d_svc_is_unitntw_group_cust_comdt_ord_inf 表的所有字段
ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_ec_group_cust_code",
  object_class="Field",
  properties={
    "fieldId": "EC_GROUP_CUST_CODE",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_comdt_specs_code",
  object_class="Field",
  properties={
    "fieldId": "COMDT_SPECS_CODE",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_comdt_ord_rltn_id",
  object_class="Field",
  properties={
    "fieldId": "COMDT_ORD_RLTN_ID",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_sale_prov",
  object_class="Field",
  properties={
    "fieldId": "SALE_PROV",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_prov_id_5",
  object_class="Field",
  properties={
    "fieldId": "PROV_ID_5",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_busi_promote_mode",
  object_class="Field",
  properties={
    "fieldId": "BUSI_PROMOTE_MODE",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_pkg_status_type",
  object_class="Field",
  properties={
    "fieldId": "PKG_STATUS_TYPE",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_prod_lvl",
  object_class="Field",
  properties={
    "fieldId": "PROD_LVL",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_ord_tm",
  object_class="Field",
  properties={
    "fieldId": "ORD_TM",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_remark",
  object_class="Field",
  properties={
    "fieldId": "REMARK",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_sign_body",
  object_class="Field",
  properties={
    "fieldId": "SIGN_BODY",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_ord_status_type_code",
  object_class="Field",
  properties={
    "fieldId": "ORD_STATUS_TYPE_CODE",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_status_chng_tm",
  object_class="Field",
  properties={
    "fieldId": "STATUS_CHNG_TM",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_cust_belo_prov_id",
  object_class="Field",
  properties={
    "fieldId": "CUST_BELO_PROV_ID",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_cust_belo_prov_id_5digits",
  object_class="Field",
  properties={
    "fieldId": "CUST_BELO_PROV_ID_5DIGITS",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_statis_ymd",
  object_class="Field",
  properties={
    "fieldId": "STATIS_YMD",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

ontology_client.create_instance(
  object_name="tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_prov_id",
  object_class="Field",
  properties={
    "fieldId": "PROV_ID",
    "dataType": "varchar(100)",
    "isNullable": True,
    "belongsToTable": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf"
  }
)

# 创建对象, 如果源表<t_order>order不存在neo4j中，则会自动创建其节点，作为Table class的一个instance
ontology_client.create_instance(
  object_name="<obj-001>全网集团客户商品订购信息",
  object_class="Object",
  properties={
    "objectOwner": "Tom",
    "objectDisplayName": "订单号",
    "objectCreatedFrom": "<t_order>order",
    "objectId": "obj-001",
    "useCase": "销售管理"
  }
)

# 创建对象属性，如果源表字段<f_order_id>order_id不存在，则会自动创建并关联至相应源表
ontology_client.create_instance(
  object_name="销售省份",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_sale_prov"
  }
)

ontology_client.create_instance(
  object_name="订购状态类型编码",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_ord_status_type_code"
  }
)

ontology_client.create_instance(
  object_name="省份标识",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_prov_id_5"
  }
)

ontology_client.create_instance(
  object_name="统计日期",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_statis_ymd"
  }
)

ontology_client.create_instance(
  object_name="业务开展模式",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_busi_promote_mode"
  }
)

ontology_client.create_instance(
  object_name="套餐状态类型",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_pkg_status_type"
  }
)

ontology_client.create_instance(
  object_name="产品等级",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_prod_lvl"
  }
)

ontology_client.create_instance(
  object_name="订购时间",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_ord_tm"
  }
)

ontology_client.create_instance(
  object_name="备注",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_remark"
  }
)

ontology_client.create_instance(
  object_name="签约主体",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_sign_body"
  }
)

ontology_client.create_instance(
  object_name="商品规格编号",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_comdt_specs_code"
  }
)

ontology_client.create_instance(
  object_name="商品订购关系ID",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_comdt_ord_rltn_id"
  }
)

ontology_client.create_instance(
  object_name="EC集团客户编码",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_ec_group_cust_code"
  }
)

ontology_client.create_instance(
  object_name="状态变更时间",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_status_chng_tm"
  }
)

ontology_client.create_instance(
  object_name="客户归属省份标识",
  object_class="ObjectField",
  properties={
    "isObjectFieldOf": "<obj-001>全网集团客户商品订购信息",
    "isObjectFieldFrom": "tw_d_svc_is_unitntw_group_cust_comdt_ord_inf_prov_id_5"
  }
)

print("样例数据已添加至neo4j图谱中")