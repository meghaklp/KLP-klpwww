use DBI;

my $data_file = $ARGV[0] || "data/school-latlon.csv";
my $output_file = "load/load-klp-coord.sql";
my $dbh = DBI->connect_cached('dbi:Oracle:host=localhost;sid=klpdb', 'klp','q1w2e3r4', { AutoCommit => 0 , RaiseError => 1 }) or die "Could not connect to the database\n";

open DATA, "$data_file" or die "cant open $data_file";
my @array_of_data = <DATA>;

open DATAOUT, ">$output_file" or die "cant open $output_file";

foreach my $line (@array_of_data)
{
  if ( $line =~ m/(.*),(.*),(.*),(.*)/i )
  {
     if( $4 eq "School" )
     {
       print DATAOUT "INSERT INTO inst_coord (schoolcode,coord) VALUES('$1',GeomFromText('POINT($2 $3)'));\n";
     }
     elsif( $4 eq "Block" ||  $4 eq "Cluster" || $4 eq "District" || $4 eq "Project")
     {
        print DATAOUT "INSERT INTO boundary_coord (id_bndry,coord,type) VALUES($1,GeomFromText('SRID=4326;POINT($2 $3)'),'$4');\n";
     }
 
  }
}
close(DATA);
close(DATAOUT);
