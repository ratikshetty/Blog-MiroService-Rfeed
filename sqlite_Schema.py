from cassandra.cluster import Cluster

cluster = Cluster(['172.17.0.2'])
session = cluster.connect('blog')

session.execute("""Create COLUMNFAMILY user(
      emailid VARCHAR,
      name VARCHAR,
      password VARCHAR,
      createdDate VARCHAR,
      modifiedDate VARCHAR,
      isDeleted INT,
      PRIMARY KEY (emailid)
);""")

session.execute("""Create COLUMNFAMILY blogData(
      Id INT,
      content VARCHAR,
      title VARCHAR,
      Author VARCHAR,
      url VARCHAR,   
      createdDate VARCHAR,
      modifiedDate VARCHAR,
      IsDeleted INT,
      comment VARCHAR,
      tag VARCHAR,
      dataType VARCHAR,
      PRIMARY KEY (dataType, id)
)WITH CLUSTERING ORDER BY (id DESC);""")

#-----------------





