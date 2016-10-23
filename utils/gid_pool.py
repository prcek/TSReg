from google.appengine.ext import db
import random
import logging
import datetime

class GidGroup(db.Model):
  group_max_value = db.IntegerProperty(default=0)
  group_new_count = db.IntegerProperty(default=0)
  group_away_count = db.IntegerProperty(default=0)
  group_dupl_count = db.IntegerProperty(default=0)


  update_ts = db.DateTimeProperty()



class GidItem(db.Model):
  usage = db.IntegerProperty(default=-1)    
  create_ts = db.DateTimeProperty()
  update_ts = db.DateTimeProperty()
  away = db.BooleanProperty(default=False)

class GidItemLog(db.Model):
  ts = db.DateTimeProperty()
  op = db.StringProperty()
  object_key = db.StringProperty()
  desc = db.StringProperty()




xg_on = db.create_transaction_options(xg=True)


def gid_group_get_or_create(key_name):
  gg = GidGroup.get_by_key_name(key_name)
  if gg is None:
    gg = GidGroup(key_name=key_name)
    gg.put()
  return gg


def gid_item_get_or_create(parent,key_name):
  gi = GidItem.get_by_key_name(key_name,parent=parent)
  if gi is None:
    gi = GidItem(parent=parent,key_name = key_name)
    gi.put()
  return gi

def put_new_item_log(parent, op, now, object_key, desc):
  gl = GidItemLog(parent=parent)
  gl.op = op
  gl.ts = now
  gl.object_key = object_key
  gl.desc = desc
  gl.put()
  return gl

def create_new_gid_item(group_name,ref_object_key=None):
  logging.info("create_new_gid_item begin")  
  now = datetime.datetime.utcnow()
  def txn():
    logging.info("transaction begin")
    gg = gid_group_get_or_create(group_name)
    logging.info("group ready")
    gg.group_max_value = gg.group_max_value + 1
    gg.group_new_count = gg.group_new_count + 1
    gg.update_ts = now
    value = gg.group_max_value
    logging.info("new value %s" %(str(value)))
    gi = GidItem(parent=gg,key_name = str(value))
    gi.usage = 1
    gi.create_ts = now
    logging.info("transaction final commit")
    gi.put()
    gg.put()
    put_new_item_log(gi,"new",now,ref_object_key,None)
    logging.info("transaction end")
    return value

  if db.is_in_transaction():
    return txn()

  val = db.run_in_transaction_options(xg_on, txn)
  return val


def ret_existing_gid_item(group_name,value,ref_object_key=None):
  logging.info("ret_existing_gid_item begin value = %d" % value)  
  now = datetime.datetime.utcnow()
  def txn():    
    logging.info("transaction begin")
    gg = gid_group_get_or_create(group_name)
    gi = GidItem.get_by_key_name(str(value),parent=gg)
    logging.info("group and item ready")
    gi.usage = gi.usage - 1
    if (gi.usage == 0):
      logging.info("item away")
      gi.away = True
      gg.group_away_count = gg.group_away_count + 1
      va = gg.group_away_count
      logging.info("new group_away_count %s" % str(va) )
      gg.update_ts = now
    elif (gi.usage == 1):
      logging.info("item no dupl")
      gg.group_dupl_count = gg.group_dupl_count - 1
      logging.info("new group_dupl_count %s" % str(gg.group_dupl_count) )
      gg.update_ts = now
    logging.info("transaction final commit")
    gi.save()
    gg.save()
    put_new_item_log(gi,"ret",now,ref_object_key,"final usage is %d" % gi.usage)
 
    logging.info("transaction end")
    return gi.usage

  if db.is_in_transaction():
    logging.info("NO TRANSACTION?")
    return txn()
  return db.run_in_transaction_options(xg_on, txn)

def ret_and_create_new_git_item(group_name,old_value,ref_object_key=None):
  logging.info("ret_and_create_new_gid_item begin old_value = %d" % old_value)  
  now = datetime.datetime.utcnow()
  def txn():    
    logging.info("transaction begin")
    gg = gid_group_get_or_create(group_name)
    gio = GidItem.get_by_key_name(str(old_value),parent=gg)
    logging.info("group and old item ready")
    gio.usage = gio.usage - 1
    gio.update_ts = now
    if (gio.usage == 0):
      logging.info("item away")
      gio.away = True
      gg.group_away_count = gg.group_away_count + 1
    elif (gio.usage == 1):
      logging.info("item no dupl")
      gg.group_dupl_count = gg.group_dupl_count - 1
      logging.info("new group_dupl_count %s" % str(gg.group_dupl_count) )

    gg.group_max_value = gg.group_max_value + 1
    gg.group_new_count = gg.group_new_count + 1
    gg.update_ts = now
    value = gg.group_max_value
    logging.info("new value %s" %(str(value)))
    gi = GidItem(parent=gg,key_name = str(value))
    gi.usage = 1
    gi.create_ts = now

    logging.info("transaction final commit")
    gi.save()
    gio.save()
    gg.save()
    put_new_item_log(gi,"new",now,ref_object_key,None)
    put_new_item_log(gio,"ret",now,ref_object_key,"final usage is %d" % gi.usage)
    return value

  if db.is_in_transaction():
    logging.info("NO TRANSACTION?")
    return txn()
  return db.run_in_transaction_options(xg_on, txn)


def put_existing_gid_item(group_name,value,ref_object_key=None):
  logging.info("put_existing_gid_item begin value = %d" % value)  
  now = datetime.datetime.utcnow()

  def txn():
    logging.info("transaction begin")
    gg = gid_group_get_or_create(group_name)
    gi = gid_item_get_or_create(gg,str(value))
    logging.info("group and item ready")
    if (gi.usage == -1):
      logging.info("new item")
      gi.usage = 1
      gi.create_ts = now
      gg.group_new_count = gg.group_new_count + 1

      if gg.group_max_value < value:
        gg.group_max_value = value

      gg.update_ts = now
        
    else:
      logging.info("item reuse")
      gi.usage = gi.usage+1
      if (gi.usage == 2):
        gg.group_dupl_count = gg.group_dupl_count + 1
        gg.update_ts = now


      gi.update_ts = now

    logging.info("transaction final commit")
    gi.put()
    gg.put()
    put_new_item_log(gi,"put",now,ref_object_key,"final usage is %d" % gi.usage)
    logging.info("transaction end")
    return gi.usage
  if db.is_in_transaction():
    logging.info("NO TRANSACTION?")
    return txn()
  return db.run_in_transaction_options(xg_on, txn)

def get_stat(group_name):
    gg = GidGroup.get_by_key_name(group_name)
    q=GidItem.all(keys_only=True)
    q.ancestor(gg)
    q.filter('usage > ', 1)

    q2=GidItem.all(keys_only=True)
    q2.ancestor(gg)
    q2.filter('away = ', True)

    return "%d  %d" % (q.count(limit=10000),q2.count(limit=10000))

def get_first_dupl(group_name):
    gg = GidGroup.get_by_key_name(group_name)
    q=GidItem.all()
    q.ancestor(gg)
    q.filter('usage > ', 1)
    o = q.get()
    if o is None:
      ref_gid = -1
    else:
      ref_gid = int(o.key().name())
    logging.info(ref_gid)
    return ref_gid


class TxnTest(db.Model):
  value_a = db.IntegerProperty(default=0)
  value_b = db.IntegerProperty(default=0)



def txn_test():

  o1 = TxnTest.get_by_key_name("obj1")
  if o1 is None:

    o1 = TxnTest(key_name="obj1")
    o1.put()



  def txn():
    logging.info("txn_test")
    o1 = TxnTest.get_by_key_name("obj1")
    logging.info("fresh o1 %d %d" % (o1.value_a,o1.value_b))
    o1.value_a = o1.value_a + 1
    logging.info("inc_a o1 %d %d" % (o1.value_a,o1.value_b))
    o1.put()
    logging.info("put_a o1 %d %d" % (o1.value_a,o1.value_b))
    o1 = TxnTest.get_by_key_name("obj1")
    logging.info("reget o1 %d %d" % (o1.value_a,o1.value_b))
    o1.value_b = o1.value_b + 1
    logging.info("inc_b o1 %d %d" % (o1.value_a,o1.value_b))
    o1.put()
    logging.info("put_b o1 %d %d" % (o1.value_a,o1.value_b))

  db.run_in_transaction_options(xg_on, txn)
