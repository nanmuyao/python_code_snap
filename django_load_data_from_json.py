import time
import json
from collections import defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from trade.pricing import get_benchmark_price
from common.helpers import decstr, getLogger, dec
from crawler.models import Symbol, Asset
from trade.models import BOrder, OrderType, OrderStatus, SubOrder
from common.tasks import send_notify_by_ding
from configuration.models import PriceSteps


def load_price_step_data():
    # 手动的吧asset和price step 对应起来
    with open("/home/haobtc/trade/asset.json",'r') as load_f:
        data = load_f.read()
        assets = json.loads(data)

    with open("/home/haobtc/trade/trade/management/commands/a.json",'r') as load_f:
        data = load_f.read()
        price_steps = json.loads(data)


    for v in price_steps:
        # 1通过price_step,找到asset_id,
        dict_fields = v.get('fields')
        asset_id = dict_fields.get('asset')
        print('asset_id', asset_id)
        for dict_asset in assets:
            # 2通过asset_id qu assets,找到name，然后去关联asset_id
            if dict_asset.get('pk') == asset_id:
                asset_name = dict_asset.get('fields').get('name')
        print('asset_name', asset_name)

        asset = Asset.objects.get(name=asset_name)
        PriceSteps.objects.create(
            asset=asset,
            extra_ratio=dict_fields.get('extra_ratio'),
            ratio=dict_fields.get('ratio'),
            max_size=dict_fields.get('max_size'),
        )
        print('end=====')


def load_asset():
    with open("/home/haobtc/trade/asset.json",'r') as load_f:
        data = load_f.read()
        datas = json.loads(data)
        for data in datas:
            params = {}
            params['id'] = data.get('pk')
            for k, v in data.get('fields').items():
                if k in ('created_at', 'updated_at'):
                    v = timezone.now()
                params[k] = v
            if params:
                #print('params==', params)
                #Asset.objects.update_or_create(
                #    name = params.get('name'),
                #    defaults = dict(
                #        id = params.get('id'),
                #        created_at = params.get('created_at'),
                #        updated_at = params.get('updated_at'),
                #        unit=params.get('unit'),
                #        status = params.get('status'),
                #    )
                #)
                #print('end')
                #continue
                try:
                    asset = Asset.objects.get(name=params.get('name'))
                    print('find', asset.id, 'data id', params.get('id'))
                    asset.created_at = params.get('created_at')
                    asset.updated_at = params.get('updated_at')
                    asset.unit = params.get('unit')
                    asset.status = params.get('status')
                    asset.save(update_fields=['created_at', 'updated_at', 'unit', 'status'])
                except Asset.DoesNotExist:
                    asset = Asset()
                    print('not find', asset.id)
                    asset.id = params.get('id')
                    asset.name = params.get('name')
                    asset.created_at = params.get('created_at')
                    asset.updated_at = params.get('updated_at')
                    asset.unit = params.get('unit')
                    asset.status = params.get('status')
                    asset.save()


class Command(BaseCommand):
    """委托单，merge_order, sub_order监控"""


    def handle(self, *args, **options):
        """统计委托单"""
        #load_asset()
        load_price_step_data()
