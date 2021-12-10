from django.db import models


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class VeloceBooksale(models.Model):
    bill_no = models.CharField(unique=True, max_length=32)
    bill_date = models.DateField()
    bill_amount = models.DecimalField(max_digits=12, decimal_places=2)
    billing_party_name = models.CharField(max_length=40)
    inquired_by = models.CharField(max_length=40)
    dealer_gst_no = models.CharField(max_length=15, blank=True, null=True)
    billing_party_gst_no = models.CharField(max_length=15, blank=True, null=True)
    upload_bill = models.CharField(max_length=100, blank=True, null=True)
    is_applied = models.BooleanField()
    is_loan_approved = models.BooleanField()
    dealers_given_finance_scheme = models.ForeignKey('VeloceDealersgivenfinancescheme', models.DO_NOTHING, blank=True, null=True)
    inquiry = models.OneToOneField('VeloceProductinquiry', models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_booksale'


class VeloceBooksaledetails(models.Model):
    inq_product_name = models.TextField()
    qty = models.IntegerField()
    inq_product_price = models.IntegerField()
    inq_product_gross_amt = models.IntegerField()
    inq_product_disc_amt = models.IntegerField()
    inq_product_tax = models.IntegerField()
    inq_product_final_amt = models.IntegerField()
    book_sale = models.ForeignKey(VeloceBooksale, models.DO_NOTHING)
    ref_inq_no = models.ForeignKey('VeloceProductinquiry', models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_booksaledetails'


class VeloceCategory(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True, null=True)
    category_img = models.CharField(max_length=100)
    slug = models.CharField(unique=True, max_length=140)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veloce_category'


class VeloceDealersgivenfinancescheme(models.Model):
    rate_of_interest = models.DecimalField(max_digits=6, decimal_places=2)
    tenure = models.IntegerField()
    is_admin_approved = models.BooleanField()
    is_admin_rejected = models.BooleanField()
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    dealer = models.ForeignKey(AuthUser, models.DO_NOTHING)
    product = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'veloce_dealersgivenfinancescheme'


class VeloceGeneralrewardpoints(models.Model):
    dealer_reward_point = models.IntegerField(blank=True, null=True)
    customer_reward_point = models.IntegerField(blank=True, null=True)
    gen_reward_start_date = models.DateTimeField()
    gen_reward_end_date = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_generalrewardpoints'


class VelocePackagingdeliverydetails(models.Model):
    selling_units = models.SmallIntegerField()
    single_package_size = models.CharField(max_length=30)
    single_gross_weight = models.CharField(max_length=30)
    package_type = models.SmallIntegerField()
    packing_size = models.CharField(max_length=30)
    packing_weight = models.CharField(max_length=30)
    picture = models.CharField(max_length=100, blank=True, null=True)
    lead_time = models.CharField(max_length=25)
    shipping_charges = models.IntegerField(blank=True, null=True)
    shipping_time = models.CharField(max_length=25)
    finance_scheme = models.BooleanField()
    product = models.OneToOneField('VeloceProduct', models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_packagingdeliverydetails'


class VelocePricestructure(models.Model):
    frequency = models.SmallIntegerField()
    label = models.CharField(max_length=25)
    amount = models.IntegerField()
    disc_per = models.IntegerField()
    disc_amt = models.IntegerField()
    amt_before_tax = models.IntegerField()
    taxes = models.IntegerField()
    final_amt = models.IntegerField()
    currency = models.SmallIntegerField()
    product = models.ForeignKey('VeloceProduct', models.DO_NOTHING)
    created_at = models.DateTimeField()
    is_visible_home = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'veloce_pricestructure'


class VeloceProduct(models.Model):
    name = models.CharField(unique=True, max_length=40)
    is_featured_product = models.BooleanField()
    specification = models.TextField(blank=True, null=True)
    slug = models.CharField(unique=True, max_length=140)
    after_warranty_service = models.CharField(max_length=60)
    local_service_location = models.CharField(max_length=40)
    showroom_location = models.CharField(max_length=40, blank=True, null=True)
    condition = models.CharField(max_length=10)
    brand_name = models.CharField(max_length=20)
    place_of_origin = models.CharField(max_length=40)
    power_watt = models.CharField(max_length=5, blank=True, null=True)
    power = models.CharField(max_length=5, blank=True, null=True)
    dimension = models.CharField(max_length=20)
    certification = models.CharField(max_length=20)
    warranty = models.IntegerField()
    after_sales_service_provided = models.CharField(max_length=60)
    engine = models.CharField(max_length=20, blank=True, null=True)
    engine_type = models.CharField(max_length=40, blank=True, null=True)
    unique_selling_point = models.CharField(max_length=40, blank=True, null=True)
    is_this_physical_product = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    category = models.ForeignKey(VeloceCategory, models.DO_NOTHING)
    sub_category = models.ForeignKey('VeloceSubcategory', models.DO_NOTHING, blank=True, null=True)
    vendor = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veloce_product'


class VeloceProductinquiry(models.Model):
    inquiry_message = models.TextField()
    is_product_bill_generated = models.BooleanField()
    inquiry_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    product = models.ForeignKey(VeloceProduct, models.DO_NOTHING)
    created_at = models.DateTimeField()
    is_product_financed = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'veloce_productinquiry'


class VeloceProductmedia(models.Model):
    image = models.CharField(max_length=100, blank=True, null=True)
    demo_video = models.CharField(max_length=100, blank=True, null=True)
    is_feature_image = models.BooleanField()
    product = models.ForeignKey(VeloceProduct, models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_productmedia'


class VeloceProductrating(models.Model):
    rated_value = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    product = models.ForeignKey(VeloceProduct, models.DO_NOTHING)
    rated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_productrating'
        unique_together = (('product', 'rated_by'),)


class VeloceProfile(models.Model):
    account_type = models.SmallIntegerField()
    is_complete = models.BooleanField()
    is_verified = models.BooleanField()
    completion_level = models.SmallIntegerField()
    verification_level = models.SmallIntegerField()
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'veloce_profile'


class VeloceRecentlyvisited(models.Model):
    visit_counter = models.IntegerField()
    last_visited = models.DateTimeField()
    category = models.ForeignKey(VeloceCategory, models.DO_NOTHING)
    product = models.ForeignKey(VeloceProduct, models.DO_NOTHING)
    sub_category = models.ForeignKey('VeloceSubcategory', models.DO_NOTHING)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'veloce_recentlyvisited'


class VeloceSale(models.Model):
    name = models.CharField(max_length=100)
    discount_type = models.SmallIntegerField()
    value = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    category = models.ForeignKey(VeloceCategory, models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(VeloceProduct, models.DO_NOTHING, blank=True, null=True)
    sub_category = models.ForeignKey('VeloceSubcategory', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_sale'


class VeloceSpecialrewardpoints(models.Model):
    dealer_reward_point = models.IntegerField(blank=True, null=True)
    customer_reward_point = models.IntegerField(blank=True, null=True)
    gen_reward_start_date = models.DateTimeField()
    gen_reward_end_date = models.DateTimeField()
    reward_to_dealer = models.OneToOneField(AuthUser, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_specialrewardpoints'


class VeloceSpecialrewardpointsRewardProduct(models.Model):
    specialrewardpoints = models.ForeignKey(VeloceSpecialrewardpoints, models.DO_NOTHING)
    product = models.ForeignKey(VeloceProduct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'veloce_specialrewardpoints_reward_product'
        unique_together = (('specialrewardpoints', 'product'),)


class VeloceSubcategory(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True, null=True)
    sub_category_img = models.CharField(max_length=100)
    slug = models.CharField(unique=True, max_length=140)
    category = models.ForeignKey(VeloceCategory, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veloce_subcategory'


class VeloceTransactionrewarddetails(models.Model):
    dealer_reward_point = models.IntegerField()
    customer_reward_point = models.IntegerField()
    transaction_date = models.DateTimeField()
    book_sale = models.ForeignKey(VeloceBooksale, models.DO_NOTHING)
    customer_rewards = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='customer_rewards')
    dealer_rewards = models.ForeignKey(AuthUser, models.DO_NOTHING, auto_created='dealer_rewards')
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_transactionrewarddetails'


class VeloceVeloceuser(models.Model):
    user_role = models.SmallIntegerField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email_address = models.CharField(unique=True, max_length=60)
    gender = models.SmallIntegerField()
    birthdate = models.DateField()
    created_at = models.DateField()
    updated_at = models.DateField()
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'veloce_veloceuser'


class VeloceVoucher(models.Model):
    discount_code = models.CharField(unique=True, max_length=32)
    discount_type = models.SmallIntegerField()
    value = models.IntegerField()
    minimum_requirement = models.SmallIntegerField()
    minimum_value = models.IntegerField()
    limit_to_one_use_per_customer = models.BooleanField(db_column='Limit_to_one_use_per_customer')  # Field name made lowercase.
    product = models.ForeignKey(VeloceProduct, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veloce_voucher'