#!/usr/bin/env perl

#
# Copyright (c) 2003-2006 University of Chicago and Fellowship
# for Interpretations of Genomes. All Rights Reserved.
#
# This file is part of the SEED Toolkit.
#
# The SEED Toolkit is free software. You can redistribute
# it and/or modify it under the terms of the SEED Toolkit
# Public License.
#
# You should have received a copy of the SEED Toolkit Public License
# along with this program; if not write to the University of Chicago
# at info@ci.uchicago.edu or the Fellowship for Interpretation of
# Genomes at veronika@thefig.info or download a copy from
# http://www.theseed.org/LICENSE.TXT.
#


use strict;
use lib::Web_Config;
use Shrub;
use Data::Dumper;

=head1 SEEDtk Server Script

This script processes a server request for Alexa. The C<action> is the intent name. The C<parameter> is the slot
content. The resulting document is a plain text string.

=cut

use constant TABLES => { Subsystem => 1, Protein => 1, Genome => 1, Feature => 1, Role => 1, Function => 1, Contig => 1 };

# Get the CGI query object.
my $cgi = CGI->new();
# This will be the result.
my $result;
# Get the intent name and parameter.
my $action = $cgi->param('action');
eval {
    # Create the Shrub object.
    my $shrub = Shrub->new();
    # Process the intent.
    if ($action eq 'GenomeIntent') {
        my $genomeID = $cgi->param('parameter');
        my ($genomeData) = $shrub->GetAll('Genome', 'Genome(id) = ?', [$genomeID], 'name contigs dna-size core');
        if (! $genomeData) {
            $result = "$genomeID does not appear in the database.";
        } else {
            my ($name, $contigs, $dnaSize, $core) = @$genomeData;
            $dnaSize = int($dnaSize / 1000);
            if ($dnaSize < 2000) {
                $dnaSize = "$dnaSize kilobases";
            } else {
                $dnaSize = int($dnaSize / 1000);
                $dnaSize = "$dnaSize megabases";
            }
            $result = "$genomeID is $name ";
            if ($core) {
                $result .= "from the core seed ";
            }
            $result .= "and has ";
            if ($contigs < 2) {
                $result .= "a single contig ";
            } else {
                $result .= "$contigs contigs ";
            }
            $result .= "and $dnaSize";
        }
    } elsif ($action eq 'CountIntent') {
        my $table = $cgi->param('parameter');
        $table =~ s/s$//;
        $table = ucfirst $table;
        if ($table eq 'Bin' || $table eq 'Ben' || $table eq 'Thing') {
            opendir(my $dh, "$FIG_Config::data/GoodPackages") || die "Could not open GoodPackages: $!";
            my @goods = grep { $_ =~ /^\d+\.\d+$/ } readdir $dh;
            my $count = scalar @goods;
            $result = "There are $count good bins in the data store.";
        } elsif (! TABLES->{$table}) {
            $result = "I don't have an object called '$table'.";
        } else {
            my $count = $shrub->GetCount($table, '', []);
            warn "Count is $count.\n";
            if ($count == 0) {
                $table .= "s";
                $result = "There are no $table in the database.";
            } elsif ($count == 1) {
                $result = "There is one $table in the database.";
            } else {
                $table .= "s";
                $result = "There are $count $table in the database.";
            }
        }
    }
};
if ($@) {
    $result = "A fatal error occurred: $@.";
}
print CGI::header('text/plain');
print $result;
