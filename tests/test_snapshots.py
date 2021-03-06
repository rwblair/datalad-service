import os
import json

import falcon
import pytest

from .dataset_fixtures import *


def test_get_snapshot(client, celery_app):
    # The main test dataset has one revision we can fetch
    response = client.simulate_get(
        '/datasets/{}/snapshots/{}'.format(DATASET_ID, SNAPSHOT_ID))
    result_doc = json.loads(response.content, encoding='utf-8')

    assert response.status == falcon.HTTP_OK
    assert result_doc['files'] == [{'filename': 'dataset_description.json', 'id': '85b9ddf2bfaf1d9300d612dc29774a98cc1d5e25', 'size': 97}] and \
            result_doc['tag'] == SNAPSHOT_ID and \
            result_doc['id'] ==  '{}:{}'.format(DATASET_ID, SNAPSHOT_ID)


def test_create_snapshot(client, new_dataset, celery_app):
    ds_id = os.path.basename(new_dataset.path)
    snapshot_id = '1'
    response = client.simulate_post(
        '/datasets/{}/snapshots/{}'.format(ds_id, snapshot_id))
    assert response.status == falcon.HTTP_OK


def test_duplicate_snapshot(client, new_dataset, celery_app):
    ds_id = os.path.basename(new_dataset.path)
    snapshot_id = '2'
    response = client.simulate_post(
        '/datasets/{}/snapshots/{}'.format(ds_id, snapshot_id))
    assert response.status == falcon.HTTP_OK
    try:
        response = client.simulate_post(
            '/datasets/{}/snapshots/{}'.format(ds_id, snapshot_id))
        assert response.status == falcon.HTTP_CONFLICT
    except:
        # In eager mode, eat the exception
        pass


def test_get_snapshots(client, new_dataset, celery_app):
    ds_id = os.path.basename(new_dataset.path)
    response = client.simulate_post(
        '/datasets/{}/snapshots/{}'.format(ds_id, 'v1.0.0'))
    assert response.status == falcon.HTTP_OK
    response = client.simulate_post(
        '/datasets/{}/snapshots/{}'.format(ds_id, 'v2.0.0'))
    assert response.status == falcon.HTTP_OK
    response = client.simulate_get(
        '/datasets/{}/snapshots'.format(ds_id))
    result_doc = json.loads(response.content, encoding='utf-8')
    assert response.status == falcon.HTTP_OK
    assert result_doc['snapshots'][0]['hexsha'] == result_doc['snapshots'][1]['hexsha']
    assert result_doc['snapshots'][0]['id'] == '{}:{}'.format(ds_id, 'v1.0.0')
    assert result_doc['snapshots'][0]['tag'] == 'v1.0.0'
    assert result_doc['snapshots'][1]['tag'] == 'v2.0.0'
