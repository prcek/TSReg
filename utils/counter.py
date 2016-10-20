from google.appengine.ext import db
import random
import logging


class SimpleCounterShard(db.Model):
  """Shards for the counter"""
  name = db.StringProperty(required=True)
  count = db.IntegerProperty(required=True, default=0)    

NUM_SHARDS = 20

def get_count(name):
  """Retrieve the value for a given sharded counter."""
  total = 0
  for counter in SimpleCounterShard.all().filter('name = ', name):
    total += counter.count
  return total
    
def increment(name):
  """Increment the value for a given sharded counter."""
  def txn():
    index = random.randint(0, NUM_SHARDS - 1)
    shard_name = name + str(index)
    counter = SimpleCounterShard.get_by_key_name(shard_name)
    if counter is None:
      counter = SimpleCounterShard(key_name=shard_name,name=name)
    counter.count += 1
    counter.put()
  db.run_in_transaction(txn)



def getNextStudentID_obs():
  increment("nextStudentId")
  val = get_count("nextStudentId")
  logging.info("getNextStudentID %d"%val)
  return val